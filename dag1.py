from datetime import datetime, timedelta
import logging
import pandas as pd
from airflow.decorators import dag, task
from airflow.providers.standard.operators.bash import BashOperator

from extractors.weather_etl   import extract_weather
from extractors.flight_etl   import extract_flight
from extractors.hotel_etl    import extract_hotel
from historical_weather_etl import hist_data
from pricing_etl import monthly_hotel_pricing, monthly_flight_pricing
from db_connector_sf import get_connection

from db_loader_sf import (
    load_weather,
    load_hotel,
    load_flight,
    load_monthly_flight,
    load_monthly_hotel,
    load_monthly_weather
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

start_date = '2026-11-28'
end_date = '2026-12-03'
dept_id = 'BOM'

destinations = {'Sikkim':'IXB','Manali':'IXC','Munnar':'COK'}

def failure_func_dag(context):
    print(f"ERROR: DAG {context['dag_run'].dag_id} failed.")
    print(f"Run Date: {context['dag_run'].execution_date}")

def failure_func_task(context):
    print(f"ERROR: Task {context['task_instance'].task_id} failed.")
    print(f"Run Date: {context['dag_run'].execution_date}")


@dag(
    dag_id="trip_helper_setup_v8",
    description="One-time load: weather, hotel, flight, monthly data, best_time for all destinations",
    start_date=datetime(2026, 6, 28),
    schedule=None,
    catchup=False,
    tags=["trip_helper", "setup"],
    on_failure_callback=failure_func_dag,
    default_args = {
         'on_failure_callback':failure_func_task,
         'sla':timedelta(8)
         }
)
def main_dag():

    @task
    def truncate_raw_tables():

        conn = get_connection()

        try:
            cursor = conn.cursor()
            tables = ["WEATHER", "HOTEL", "FLIGHT","MONTHLY_WEATHER","MONTHLY_FLIGHT","MONTHLY_HOTEL"]
            for table in tables:
                cursor.execute(f"TRUNCATE TABLE IF EXISTS RAW.{table}")

        finally:
            cursor.close()
            conn.close()

    @task
    def run_hotel(destination):
        df = extract_hotel(destination,start_date,end_date)
        load_hotel(df)
    
    @task
    def run_flight(destination, arr_id):
        df = extract_flight(dept_id, arr_id, start_date, end_date,location=destination)
        load_flight(df)

    @task
    def run_weather(destination):
        df = extract_weather(destination)
        load_weather(df)

    @task
    def run_monthly_flight(destination,arr_id):
        df = monthly_flight_pricing(dept_id,arr_id,location=destination)
        load_monthly_flight(df)

    @task
    def run_monthly_hotel(destination):
        df = monthly_hotel_pricing(destination)
        load_monthly_hotel(df)

    @task
    def run_monthly_weather(destination):
        df = hist_data(destination)
        load_monthly_weather(df)


    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="""
        set -e

        cd /opt/airflow/dags/tour_helper_dbt

        dbt build \
            --profiles-dir /opt/airflow/.dbt \
            --target dev
        """,
        retries=1,
        retry_delay=timedelta(minutes=2),
    )

    truncate = truncate_raw_tables()
    all_tasks= []
    for destination,arr_id in destinations.items():
        dest_low = destination.lower()  

        hotel = run_hotel.override(task_id=f"run_hotel_{dest_low}")(destination)
        flight = run_flight.override(task_id=f"run_flight_{dest_low}")(destination,arr_id)
        weather = run_weather.override(task_id=f"run_weather_{dest_low}")(destination)

        monthly_hotel = run_monthly_hotel.override(task_id=f"run_monthly_hotel_{dest_low}")(destination)
        monthly_flight = run_monthly_flight.override(task_id=f"run_monthly_flight_{dest_low}")(destination,arr_id)
        monthly_weather = run_monthly_weather.override(task_id=f"run_monthly_weather_{dest_low}")(destination)
        
        tasks = [hotel, flight, weather, monthly_hotel,monthly_flight,monthly_weather]
        truncate >> tasks
        all_tasks.extend(tasks)
    all_tasks >> dbt_build

main_dag()

