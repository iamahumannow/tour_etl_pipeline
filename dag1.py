from datetime import datetime, timedelta
import logging
import pandas as pd

from io import BytesIO
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

from extractors.weather_etl   import extract_weather
from extractors.flight_etl   import extract_flight
from extractors.hotel_etl    import extract_hotel
from historical_weather_etl import hist_data
from pricing_etl import monthly_hotel_pricing, monthly_flight_pricing
from pipeline_2 import compute_best_time

from db_loader import (
    load_weather,
    load_hotel,
    load_flight,
    load_monthly_flight,
    load_monthly_hotel,
    load_monthly_weather,
    load_best_time,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

start_date = '2026-11-28'
end_date = '2026-12-03'
dept_id = 'BOM'

destinations = {'Sikkim':'IXB','Manali':'IXC','Munnar':'COK'}

def upload_df(df,name):
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)

        obj_name = f"monthly_data/{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.parquet"
        
        s3_hook = S3Hook(aws_conn_id="minio_conn")
        s3_hook.load_file_obj(
            file_obj=parquet_buffer,
            key=obj_name,
            bucket_name="airflow-bucket",
            replace=True
        )
        
        return obj_name

def download_df(obj_name):
        s3_hook = S3Hook(aws_conn_id="minio_conn")
        
        s3_obj = s3_hook.get_key(key=obj_name, bucket_name="airflow-bucket")
        file_bytes = s3_obj.get()["Body"].read()
        
        df = pd.read_parquet(BytesIO(file_bytes))
        return df

def failure_func_dag(context):
    print(f"ERROR: DAG {context['dag_run'].dag_id} failed.")
    print(f"Run Date: {context['dag_run'].execution_date}")

def failure_func_task(context):
    print(f"ERROR: Task {context['task_instance'].task_id} failed.")
    print(f"Run Date: {context['dag_run'].execution_date}")



@dag(
    dag_id="trip_helper_setup_v5",
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
        cntx = get_current_context()
        curr_id = cntx['task_instance'].task_id
        df = monthly_flight_pricing(dept_id,arr_id,location=destination)
        load_monthly_flight(df)
        return upload_df(df,curr_id)

    @task
    def run_monthly_hotel(destination):
        cntx = get_current_context()
        curr_id = cntx['task_instance'].task_id
        df = monthly_hotel_pricing(destination)
        load_monthly_hotel(df)
        return upload_df(df,curr_id)

    @task
    def run_monthly_weather(destination):
        cntx = get_current_context()
        curr_id = cntx['task_instance'].task_id
        df = hist_data(destination)
        load_monthly_weather(df)
        return upload_df(df,curr_id)
    
    @task
    def run_best_time(destination,mh_path,mf_path,mw_path):
        w_df = download_df(mw_path)
        f_df = download_df(mf_path)
        h_df = download_df(mh_path)
        df = compute_best_time(destination,w_df,f_df,h_df)
        load_best_time(df)
        print("Best Time calculation is completed")


    for destination,arr_id in destinations.items():
        dest_low = destination.lower()  

        run_hotel.override(task_id=f"run_hotel_{dest_low}")(destination)
        run_flight.override(task_id=f"run_flight_{dest_low}")(destination,arr_id)
        run_weather.override(task_id=f"run_weather_{dest_low}")(destination)

        mh_path = run_monthly_hotel.override(task_id=f"run_monthly_hotel_{dest_low}")(destination)
        mf_path = run_monthly_flight.override(task_id=f"run_monthly_flight_{dest_low}")(destination,arr_id)
        mw_path = run_monthly_weather.override(task_id=f"run_monthly_weather_{dest_low}")(destination)

        run_best_time.override(task_id=f"run_best_time_{dest_low}")(destination,mh_path,mf_path,mw_path)

main_dag()

