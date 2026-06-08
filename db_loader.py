import logging
import pandas as pd
from db_connector import get_engine

logging.basicConfig(
    filename="db_loader.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def _load(df: pd.DataFrame, table_name: str) -> None:
    if df is None or df.empty:
        logging.warning(f"[{table_name}] Empty DataFrame, skipping load")
        return

    df = df.copy()
    df["fetched_at"] = pd.Timestamp.now()

    try:
        engine = get_engine()
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="append", 
            index=False           
        )
        logging.info(
            f"[{table_name}] Loaded {len(df)} rows successfully."
        )
    except Exception as e:
        logging.error(f"[{table_name}] Load failed: {e}")
        raise


def load_weather(df: pd.DataFrame) -> None:
    _load(df, "weather")


def load_flight(df: pd.DataFrame) -> None:
    _load(df, "flight")


def load_hotel(df: pd.DataFrame) -> None:
    _load(df, "hotel")
