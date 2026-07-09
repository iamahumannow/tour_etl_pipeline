import os
from logger import get_logger
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
from db_connector import get_engine
logging = get_logger("mysql_to_snowflake", "mysql_to_snowflake.log")

load_dotenv()

TABLES = [
    "weather",
    "monthly_weather",
    "flight",
    "monthly_flight",
    "hotel",
    "monthly_hotel",
    "hist_flight"
]


def get_snowflake_engine():
    return create_engine(
        "snowflake://{user}:{password}@{account}/{database}/{schema}"
        "?warehouse={warehouse}".format(
            user=os.getenv("SF_USER"),
            password=os.getenv("SF_PASSWORD"),
            account=os.getenv("SF_ACCOUNT"),
            database=os.getenv("SF_DATABASE"),
            schema=os.getenv("SF_SCHEMA", "RAW"),
            warehouse=os.getenv("SF_WAREHOUSE"),
        )
    )


def migrate_table(table: str, mysql_engine, sf_engine):
    logging.info(f"[{table}] Reading from MySQL...")

    try:
        df = pd.read_sql(f"SELECT * FROM {table}", mysql_engine)
    except Exception as e:
        logging.error(f"[{table}] MySQL read failed: {e}")
        raise

    if df.empty:
        logging.warning(f"[{table}] Table is empty in MySQL — skipping.")
        return

    logging.info(f"[{table}] {len(df)} rows read. Writing to Snowflake...")

    # Snowflake is case-insensitive but uppercases everything by default
    # keeping columns lowercase avoids surprises in dbt later
    df.columns = [col.lower() for col in df.columns]

    try:
        df.to_sql(
            name=table.lower(),
            con=sf_engine,
            if_exists="replace",   # safe for one-time load — replaces if re-run
            index=False,
            chunksize=1000,        # writes in batches — avoids memory issues
        )
        logging.info(f"[{table}] Successfully loaded {len(df)} rows.")
    except Exception as e:
        logging.error(f"[{table}] Snowflake write failed: {e}")
        raise


def run():
    logging.info("Starting MySQL to Snowflake migration...")

    mysql_engine = get_engine()
    sf_engine    = get_snowflake_engine()

    success = []
    failed  = []

    for table in TABLES:
        try:
            migrate_table(table, mysql_engine, sf_engine)
            success.append(table)
        except Exception:
            failed.append(table)
            logging.warning(f"[{table}] Skipping due to error — continuing with remaining tables.")

    # ── summary ───────────────────────────────────────────────
    logging.info("=" * 50)
    logging.info(f"Migration complete.")
    logging.info(f"Succeeded : {len(success)} tables — {success}")

    if failed:
        logging.error(f"Failed : {len(failed)} tables — {failed}")
    else:
        logging.info("All tables migrated successfully.")
    logging.info("\n")


if __name__ == "__main__":
    run()