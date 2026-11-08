from datetime import datetime

from google.cloud import bigquery
from pyspark.sql.functions import col, lit, current_timestamp

from utils.spark_session import get_spark_session
from utils.bigquery_io import get_max_ingested_at, merge_scd2, insert_new_versions, write_to_bigquery

BRONZE_TABLE = "a3-retail-dwh-project.bronze_layer.ward"
SILVER_TABLE = "a3-retail-dwh-project.silver_layer.ward"
STAGING_TABLE = "a3-retail-dwh-project.silver_layer.ward_staging"
WATERMARK_COLUMN = "bronze_ingested_at"


def transform_ward():
    spark = get_spark_session("transform_ward")
    client = bigquery.Client()

    df = bronze_change_data_captured(spark, client)
    df = silver_transform_ward(df)
    merge_into_silver(client, df)


def merge_into_silver(client, df):
    write_to_bigquery(df, STAGING_TABLE, mode="overwrite")

    insert_columns = {
        "ward_sk": "GENERATE_UUID()",
        "ward_id": "source.ward_id",
        "ward_name": "source.ward_name",
        "ward_full_name": "source.ward_full_name",
        "ward_type": "source.ward_type",
        "province_id": "source.province_id",
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
        key_column="ward_id",
        compare_columns=[
            "ward_name",
            "ward_full_name",
            "ward_type",
            "province_id",
            "latitude",
            "longitude",
        ],
    )

    insert_new_versions(
        client,
        target_table=SILVER_TABLE,
        staging_table=STAGING_TABLE,
        key_column="ward_id",
        insert_columns=insert_columns,
    )


def silver_transform_ward(df):
    df = df.withColumn("silver_ingested_at", current_timestamp()) \
        .withColumn("valid_from_date", current_timestamp()) \
        .withColumn("valid_to_date", lit(None).cast("timestamp")) \
        .withColumn("is_current", lit(True))

    df = df.select(
        col("ward_code").alias("ward_id"),
        col("ward_name"),
        col("ward_full_name"),
        col("ward_type"),
        col("province_code").alias("province_id"),
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
    transform_ward()
