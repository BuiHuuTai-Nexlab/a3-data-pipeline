from pyspark.sql import functions as F
from utils.spark_session import get_spark_session
from utils.google_sheet_reader import read_merchant_sheet
from utils.bigquery_io import write_to_bigquery, get_max_ingested_at

TABLE_ID = "a3-retail-dwh-project.bronze_layer.merchant"

def ingest_merchant():
    spark = get_spark_session("ingest_merchant")
    df = read_merchant_sheet(spark)
    df = df.withColumn("ingested_at", F.col("ingested_at").cast("timestamp"))
    df = df.withColumn("source_record_count", F.col("source_record_count").cast("integer"))

    watermark = get_max_ingested_at(TABLE_ID)
    if watermark:
        df = df.filter(F.col("ingested_at") >= F.lit(watermark))

    df = df.withColumn("bronze_loaded_at", F.current_timestamp())

    write_to_bigquery(df, TABLE_ID, mode="append")

if __name__ == "__main__":
    ingest_merchant()
