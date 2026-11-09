from src.bronze.ingest_merchant import ingest_merchant
from src.silver.transform_province import transform_province
from src.silver.transform_ward import transform_ward
from src.silver.transform_merchant import transform_merchant
from utils.spark_session import get_spark_session


def run_pipeline():
    spark = get_spark_session("a3_pipeline")

    ingest_merchant(spark)
    transform_province(spark)
    transform_ward(spark)
    transform_merchant(spark)


if __name__ == "__main__":
    run_pipeline()
