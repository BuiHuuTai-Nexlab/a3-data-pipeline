from datetime import datetime

from google.cloud import bigquery
from pyspark.sql.functions import col, lit, current_timestamp

from utils.spark_session import get_spark_session
from utils.bigquery_io import get_max_ingested_at, merge_scd2, insert_new_versions, write_to_bigquery

BRONZE_TABLE = "a3-retail-dwh-project.bronze_layer.province"
SILVER_TABLE = "a3-retail-dwh-project.silver_layer.province"
STAGING_TABLE = "a3-retail-dwh-project.silver_layer.province_staging"
WATERMARK_COLUMN = "bronze_ingested_at"


def transform_province(spark):
    client = bigquery.Client()

    df = bronze_change_data_captured(spark, client)
    df = silver_transform_province(df)
    merge_into_silver(client, df)


def merge_into_silver(client, df):
    write_to_bigquery(df, STAGING_TABLE, mode="overwrite")

    insert_columns = {
        "province_sk": "GENERATE_UUID()",
        "province_id": "source.province_id",
        "province_name": "source.province_name",
        "province_full_name": "source.province_full_name",
        "province_type": "source.province_type",
        "region_name": "source.region_name",
        "latitude": "source.latitude",
        "longitude": "source.longitude",
        "bronze_ingested_at": "source.bronze_ingested_at",
        "silver_ingested_at": "source.silver_ingested_at",
        "valid_from_date": "CURRENT_TIMESTAMP()",
        "valid_to_date": "NULL",
        "is_current": "TRUE",
    }

    merge_scd2(
        client,
        target_table=SILVER_TABLE,
        staging_table=STAGING_TABLE,
        key_column="province_id",
        compare_columns=[
            "province_name",
            "province_full_name",
            "province_type",
            "region_name",
            "latitude",
            "longitude",
        ],
    )

    insert_new_versions(
        client,
        target_table=SILVER_TABLE,
        staging_table=STAGING_TABLE,
        key_column="province_id",
        insert_columns=insert_columns,
    )


def silver_transform_province(df):
    df = df.withColumn("silver_ingested_at", current_timestamp()) \
        .withColumn("valid_from_date", current_timestamp()) \
        .withColumn("valid_to_date", lit(None).cast("timestamp")) \
        .withColumn("is_current", lit(True))

    df = df.select(
        col("province_code").alias("province_id"),
        col("province_name"),
        col("province_full_name"),
        col("province_type"),
        col("region_name"),
        col("latitude"),
        col("longitude"),
        col("bronze_ingested_at"),
        col("silver_ingested_at"),
        col("valid_from_date"),
        col("valid_to_date"),
        col("is_current"),
    )
    return df


def bronze_change_data_captured(spark, client):
    silver_watermark = get_max_ingested_at(client, WATERMARK_COLUMN, SILVER_TABLE) or datetime(1990, 11, 11)

    df = spark.read.format("bigquery") \
        .load(BRONZE_TABLE) \
        .filter(col("bronze_ingested_at") > lit(silver_watermark).cast("timestamp"))
    return df


if __name__ == "__main__":
    transform_province(get_spark_session("transform_province"))
