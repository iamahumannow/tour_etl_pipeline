import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

load_dotenv()

def get_engine():
    user     = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD"))
    host     = os.getenv("DB_HOST", "localhost")
    port     = os.getenv("DB_PORT", "3306")
    db       = os.getenv("DB_NAME")

    connection_url = (
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    )

    engine = create_engine(
        connection_url,
        pool_pre_ping=True 
    )
    return engine

def test_connection():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connection successful.")
    except Exception as e:
        print(f"Connection failed: {e}")


# if __name__ == "__main__":
#     test_connection()

