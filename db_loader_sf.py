import pandas as pd
from snowflake.connector.pandas_tools import write_pandas

from logger import get_logger
from db_connector_sf import get_connection

logging = get_logger("db_loader_sf", "db_loader_sf.log")


def _load(df, table_name):

    if df is None or df.empty:
        logging.warning(f"[{table_name}] Empty DataFrame, skipping load")
        return

    df = df.copy()
    df["FETCHED_AT"] = pd.Timestamp.now()
    df.columns = [c.upper() for c in df.columns]

    try:
        conn = get_connection()
        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name.upper(),
            schema="RAW",
            auto_create_table=False,
            overwrite=False,
            use_logical_type=True
        )

        if success:
            logging.info(
                f"[{table_name}] Loaded {nrows} rows in {nchunks} chunk(s)."
            )
        else:
            raise Exception("write_pandas returned success=False")

    except Exception as e:
        logging.error(f"[{table_name}] Load failed: {e}")
        raise
    
    finally:
        if conn:
            conn.close()



def load_weather(df):
    _load(df, "weather")


def load_flight(df):
    _load(df, "flight")


def load_hotel(df):
    _load(df, "hotel")


def load_monthly_flight(df):
    _load(df, "monthly_flight")


def load_monthly_hotel(df):
    _load(df, "monthly_hotel")


def load_monthly_weather(df):
    _load(df, "monthly_weather")


def load_hist_flight(df):
    _load(df, "hist_flight")

logging.info("\n")