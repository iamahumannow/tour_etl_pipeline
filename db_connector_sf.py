import os
from logger import get_logger
from dotenv import load_dotenv
import snowflake.connector
from cryptography.hazmat.primitives import serialization

logging = get_logger("db_connector_sf", "db_connector_sf.log")

load_dotenv()

def get_connection():
    try:
        private_key_path = os.getenv("SF_PRIVATE_KEY_PATH")

        with open(private_key_path, "rb") as key:
            p_key = serialization.load_pem_private_key(
                key.read(),
                password=None
            )

        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        conn = snowflake.connector.connect(
            user=os.getenv("SF_USER"),
            account=os.getenv("SF_ACCOUNT"),
            warehouse=os.getenv("SF_WAREHOUSE", "DBT_WH"),
            database=os.getenv("SF_DATABASE", "DEV_DB"),
            schema=os.getenv("SF_SCHEMA", "RAW"),
            role=os.getenv("SF_ROLE", "ACCOUNTADMIN"),
            private_key=pkb,
        )
        logging.info("Successfully connected to Snowflake.")
        return conn

    except Exception as e:
        logging.error(f"Failed to create Snowflake engine via Key-Pair Auth: {e}")
        raise

