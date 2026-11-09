from src.bronze.ingest_merchant import ingest_merchant
from src.silver.transform_province import transform_province
from src.silver.transform_ward import transform_ward
from src.silver.transform_merchant import transform_merchant
from utils.logger import get_logger
from utils.spark_session import get_spark_session

logger = get_logger("run_pipeline")


def run_step(name, step, spark):
    logger.info(f"Start {name}")
    try:
        step(spark)
    except Exception:
        logger.exception(f"Failed {name}")
        raise  # de batch bao FAILED va workflow dung lai
    logger.info(f"Done {name}")


def run_pipeline():
    spark = get_spark_session("a3_pipeline")

    run_step("ingest_merchant", ingest_merchant, spark)
    run_step("transform_province", transform_province, spark)
    run_step("transform_ward", transform_ward, spark)
    run_step("transform_merchant", transform_merchant, spark)


if __name__ == "__main__":
    run_pipeline()
