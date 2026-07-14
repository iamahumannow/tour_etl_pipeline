import os
from logger import get_logger
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
from db_connector import get_engine

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

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
    try:
        account = os.getenv("SF_ACCOUNT")
        user = os.getenv("SF_USER")
        database = os.getenv("SF_DATABASE", "RAW_DB")
        schema = os.getenv("SF_SCHEMA", "MYSQL_STAGE")
        warehouse = os.getenv("SF_WAREHOUSE", "DBT_WH")
        role = os.getenv("SF_ROLE", "ACCOUNTADMIN")

        private_key_path = os.getenv("SF_PRIVATE_KEY")
        private_key_passphrase = os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE")

        if not private_key_path:
            raise ValueError("SNOWFLAKE_PRIVATE_KEY_PATH must be provided for key-pair authentication.")

        logging.info(f"Loading private key file from: {private_key_path}")
        with open(private_key_path, "rb") as key_file:
            passphrase_bytes = private_key_passphrase.encode() if private_key_passphrase else None
            p_key = serialization.load_pem_private_key(
                key_file.read(),
                password=passphrase_bytes,
                backend=default_backend()
            )

        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        connection_url = f"snowflake://{user}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}"
        
        return create_engine(
            connection_url,
            connect_args={
                'private_key': pkb
            }
        )
    except Exception as e:
        logging.error(f"Failed to create Snowflake engine via Key-Pair Auth: {e}")
        raise


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


    df.columns = [col.lower() for col in df.columns]

    try:
        df.to_sql(
            name=table.lower(),
            con=sf_engine,
            if_exists="replace",   
            index=False,
            chunksize=1000,       
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

    logging.info("-" * 50)
    logging.info(f"Migration complete.")
    logging.info(f"Succeeded : {len(success)} tables — {success}")

    if failed:
        logging.error(f"Failed : {len(failed)} tables — {failed}")
    else:
        logging.info("All tables migrated successfully.")
    logging.info("\n")


if __name__ == "__main__":
    run()