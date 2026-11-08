import os
import sys

from dotenv import load_dotenv
from pyspark.sql import SparkSession

load_dotenv(override=True)
hadoop_home = os.environ.get("HADOOP_HOME")
if hadoop_home:
    os.environ["PATH"] += f";{hadoop_home}\\bin"

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def get_spark_session(app_name: str) -> SparkSession:
    spark = SparkSession\
            .builder \
            .appName(app_name) \
            .master("local[4]") \
            .config("spark.driver.bindAddress", "127.0.0.1") \
            .config("spark.driver.host", "127.0.0.1") \
            .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.41.1,javax.inject:javax.inject:1") \
            .getOrCreate()
            # .config("spark.executor.memory", "2g") \
            # .config("spark.driver.memory", "1g") \
            # .config("spark.executor.cores", "2") \
    return spark
