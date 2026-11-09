import subprocess
import sys
from datetime import datetime

try:
    from vietnamadminunits import convert_address
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "vietnamadminunits"])
    from vietnamadminunits import convert_address

from google.cloud import bigquery
from pyspark.sql.functions import col, lit, current_timestamp, udf
from pyspark.sql.types import StructType, StructField, StringType

from utils.spark_session import get_spark_session
from utils.bigquery_io import get_max_ingested_at, merge_scd2, insert_new_versions, write_to_bigquery

BRONZE_TABLE = "a3-retail-dwh-project.bronze_layer.merchant"
SILVER_TABLE = "a3-retail-dwh-project.silver_layer.merchant"
STAGING_TABLE = "a3-retail-dwh-project.silver_layer.merchant_staging"
WATERMARK_COLUMN = "bronze_ingested_at"

ADMIN_UNIT_SCHEMA = StructType([
    StructField("ward_code", StringType()),
    StructField("province_code", StringType()),
])


def _with_unit_prefix(name, prefix):
    if name and name.strip().isdigit():
        return f"{prefix} {name.strip()}"
    return name


@udf(returnType=ADMIN_UNIT_SCHEMA)
def resolve_admin_unit(ward_name, district_name, province_name):
    if not province_name:
        return (None, None)

    ward_name = _with_unit_prefix(ward_name, "Phường")
    district_name = _with_unit_prefix(district_name, "Quận")
    address = ", ".join(part for part in [ward_name, district_name, province_name] if part)

    try:
        result = convert_address(address, mode="CONVERT_2025")
    except Exception:
        return (None, None)
    return (result.ward_code, result.province_code)


def transform_merchant(spark):
    client = bigquery.Client()

    df = bronze_change_data_captured(spark, client)
    df = silver_transform_merchant(df)
    merge_into_silver(client, df)


def merge_into_silver(client, df):
    write_to_bigquery(df, STAGING_TABLE, mode="overwrite")

    insert_columns = {
        "merchant_sk": "GENERATE_UUID()",
        "merchant_id": "source.merchant_id",
        "phone": "source.phone",
        "phone_carrier": "source.phone_carrier",
        "merchant_name": "source.merchant_name",
        "address": "source.address",
        "ward_id": "source.ward_id",
        "province_id": "source.province_id",
        "category_l1_name": "source.category_l1_name",
        "category_l2_name": "source.category_l2_name",
        "ingested_at": "source.ingested_at",
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
        key_column="merchant_id",
        compare_columns=[
            "phone",
            "phone_carrier",
            "merchant_name",
            "address",
            "ward_id",
            "province_id",
            "category_l1_name",
            "category_l2_name",
        ],
    )

    insert_new_versions(
        client,
        target_table=SILVER_TABLE,
        staging_table=STAGING_TABLE,
        key_column="merchant_id",
        insert_columns=insert_columns,
    )


def silver_transform_merchant(df):
    df = df.withColumn("admin_unit", resolve_admin_unit("ward_name", "district_name", "province_name"))
    df = df.withColumn("ward_id", col("admin_unit.ward_code").cast("int"))
    df = df.withColumn("province_id", col("admin_unit.province_code").cast("int"))

    df = df.withColumn("silver_ingested_at", current_timestamp()) \
        .withColumn("valid_from_date", current_timestamp()) \
        .withColumn("valid_to_date", lit(None).cast("timestamp")) \
        .withColumn("is_current", lit(True))

    df = df.select(
        col("merchant_id"),
        col("phone_e164").alias("phone"),
        col("phone_carrier"),
        col("merchant_name"),
        col("street_address").alias("address"),
        col("ward_id"),
        col("province_id"),
        col("category_l1_name"),
        col("category_l2_name"),
        col("ingested_at"),
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
    transform_merchant(get_spark_session("transform_merchant"))
