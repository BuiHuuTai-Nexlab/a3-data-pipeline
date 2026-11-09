from dotenv import find_dotenv, load_dotenv
from pyspark.sql import SparkSession

load_dotenv(find_dotenv(usecwd=True), override=True)

BIGQUERY_CONNECTOR_PACKAGES = (
    "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.41.1,"
    "javax.inject:javax.inject:1"
)


def get_spark_session(app_name: str) -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[4]")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.jars.packages", BIGQUERY_CONNECTOR_PACKAGES)
        .getOrCreate()
    )
