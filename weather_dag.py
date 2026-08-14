from datetime import datetime, timedelta
from logger import get_logger

from airflow.decorators import dag, task
from airflow.providers.standard.operators.bash import BashOperator

from extractors.weather_etl import extract_weather
from db_loader_sf import load_weather
from db_connector_sf import get_connection

logging = get_logger("weather_dag", "weather_dag.log")

start_date = '2026-11-28'
end_date = '2026-12-03'
dept_id = 'BOM'

destinations = {'sikkim':'IXB'}

@dag (
    dag_id = 'weather_dag_v4',
    start_date = datetime(2026, 7, 21),
    catchup = False,
    schedule = None,
    tags = ['trip_helper', 'debug']
)
def main_dag():

    # @task
    # def truncate_raw_tables():

    #     conn = get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute("""
    #                 SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE(), CURRENT_ROLE(), count(*) from RAW.WEATHER;
    #                 """)

    #     logging.info(cursor.fetchone())
    #     try:
            
    #         tables = ["WEATHER"]
    #         for table in tables:
    #             cursor.execute(f"SELECT COUNT(*) FROM RAW.{table}")
    #             before = cursor.fetchone()[0]

    #             cursor.execute(f"TRUNCATE TABLE RAW.{table}")

    #             cursor.execute(f"SELECT COUNT(*) FROM RAW.{table}")
    #             after = cursor.fetchone()[0]

    #             logging.info(f"{table}: {before} -> {after}")

    #     finally:
    #         cursor.close()
    #         conn.close()
    

    @task
    def run_weather(destination):
        df = extract_weather(destination)
        load_weather(df)

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="""
        set -e

        cd /opt/airflow/dags/tour_helper_dbt

        dbt build \
            --select stg_weather \
            --profiles-dir /opt/airflow/.dbt \
            --target dev
        """,
        retries=1,
        retry_delay=timedelta(minutes=2),
    )

    # truncate = truncate_raw_tables()
    all_tasks= []
    for destination,arr_id in destinations.items():
        dest_low = destination.lower()
        weather_task = run_weather.override(task_id=f"run_weather_{dest_low}")(destination)

        # truncate >> weather_task
        all_tasks.extend([weather_task])
    all_tasks >> dbt_build

main_dag()
