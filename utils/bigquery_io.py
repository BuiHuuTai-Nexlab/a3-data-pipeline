from utils.logger import get_logger
logger = get_logger(__name__) 
from google.cloud import bigquery

def get_max_ingested_at(table_id):
    client = bigquery.Client()
    query = f"SELECT MAX(ingested_at) AS watermark FROM `{table_id}`"
    try:
        watermark = list(client.query(query).result())[0].watermark
        return watermark
    except Exception:
        return None

def write_to_bigquery(df, table_id, mode="overwrite"):
    try:
        df.write \
            .format("bigquery") \
            .option("table", table_id) \
            .option("writeMethod", "direct") \
            .mode(mode) \
            .save()
        logger.info(f"Wrote data to {table_id} (mode={mode})")
    except Exception:
        logger.exception(f"Failed to write to {table_id}")
        raise
