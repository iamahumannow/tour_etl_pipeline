from datetime import datetime, timedelta
from airflow.sdk import dag, task
from airflow.providers.standard.operators.bash import BashOperator
import pandas as pd

from pipeline_3 import run
from extractors.flight_etl import extract_flight
from db_loader_sf import load_hist_flight


dept_id = 'BOM'
outbound_date = '2026-11-19'
return_date = '2026-11-24'

destinations = {'Sikkim':'IXB','Varkala':'TRV'}


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
    def run_flight_tracker(arr_id,location):
        df = extract_flight(dept_id, arr_id, outbound_date, return_date, location)
        load_hist_flight(df)

    dbt_build = BashOperator(
            task_id="dbt_build",
            bash_command="""
            set -e
    
            cd /opt/airflow/dags/tour_helper_dbt
    
            dbt build \
                --select stg_hist_flight, mart_hist_flight\
                --profiles-dir /opt/airflow/.dbt \
                --target dev
            """,
            retries=1,
            retry_delay=timedelta(minutes=2),
        )

    for destination,arr_id in destinations.items():
        dest_low = destination.lower()
        flight = run_flight_tracker.override(task_id=f"run_flight_tracker_{dest_low}")(arr_id,destination)
    flight >> dbt_build
    
main_dag()