from datetime import datetime, timedelta
from airflow.sdk import dag, task
import pandas as pd

from pipeline_3 import run
from extractors.flight_etl import extract_flight
from db_loader import load_hist_flight


arr_id = {'IXB':'Sikkim','TRV':'Varkala'}
dept_id = 'BOM'
outbound_date = '2026-11-19'
return_date = '2026-11-24'

def failure_func_dag(context):
    print(f"ERROR: DAG {context['dag_run'].dag_id} failed.")
    print(f"Run Date: {context['dag_run'].execution_date}")

def failure_func_task(context):
    print(f"ERROR: Task {context['task_instance'].task_id} failed.")
    print(f"Run Date: {context['dag_run'].execution_date}")

@dag(
    dag_id = 'flight_price_tracker_v2',
    description = 'Creating scheduled DAG instead of Task scheduler (cron job)',
    start_date  = datetime(2026,7,1),
    schedule = '0 19 * * 1,3,5',
    catchup = False,
    tags = ['trip_helper'],
    on_failure_callback=failure_func_dag,
    default_args = {'on_failure_callback':failure_func_task,'sla':timedelta(8)}
)
def main_dag():
    @task
    def run_flight_tracker():
        run(arr_id,dept_id,outbound_date,return_date)
    run_flight_tracker()
main_dag()