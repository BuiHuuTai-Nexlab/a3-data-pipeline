from pathlib import Path

from google.cloud import bigquery

from utils.logger import get_logger

logger = get_logger(__name__)

SQL_DIR = Path(__file__).resolve().parents[2] / "sql" / "gold"

# Thu tu quan trong: bang nao tro toi bang khac (FK) phai chay sau.
DIM_ORDER = [
    "dim_province",
    "dim_ward",
    "dim_category",
    "dim_phone",
    "dim_address",
    "dim_merchant",
]


def run_gold():
    client = bigquery.Client()

    for name in DIM_ORDER:
        sql = (SQL_DIR / f"{name}.sql").read_text(encoding="utf-8")
        client.query(sql).result()
        logger.info(f"Built gold_layer.{name}")


if __name__ == "__main__":
    run_gold()
