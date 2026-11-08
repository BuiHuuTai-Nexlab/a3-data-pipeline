from utils.logger import get_logger

logger = get_logger(__name__)


def get_max_ingested_at(client, watermark_column: str, table_id: str):
    query = f"SELECT MAX({watermark_column}) AS watermark FROM `{table_id}`"
    try:
        watermark = list(client.query(query).result())[0].watermark
        return watermark
    except Exception:
        return None


def merge_scd2(client, target_table, staging_table, key_column, compare_columns):
    changed = " OR ".join(f"target.{c} != source.{c}" for c in compare_columns)
    client.query(f"""
        MERGE `{target_table}` AS target
        USING `{staging_table}` AS source
        ON target.{key_column} = source.{key_column}
        WHEN MATCHED AND target.is_current = TRUE AND ({changed}) THEN
            UPDATE SET is_current = FALSE, valid_to_date = CURRENT_TIMESTAMP()
    """).result()


def insert_new_versions(client, target_table, staging_table, key_column, insert_columns: dict):
    columns = ", ".join(insert_columns.keys())
    values = ", ".join(insert_columns.values())
    client.query(f"""
        INSERT INTO `{target_table}` ({columns})
        SELECT {values}
        FROM `{staging_table}` AS source
        LEFT JOIN `{target_table}` AS target
            ON target.{key_column} = source.{key_column} AND target.is_current = TRUE
        WHERE target.{key_column} IS NULL
    """).result()


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
