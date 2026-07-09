from datetime import datetime, timedelta

import csv
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook


def_args = {
    'owner' : 'me',
    'retries' : 3,
    'retry_delay' : timedelta(minutes=5)
}


def mysql_to_csv(ds_nodash):
    hook = MySqlHook(
        mysql_conn_id = 'mysql_local'
    )
    res = hook.get_records(sql= 'select * from orders limit 50')
    with open(f"/opt/airflow/dags/get_orders_{ds_nodash}.txt", "w") as f:
        x = csv.writer(f)
        x.writerows(res)
    print(f'saved successfully in: {ds_nodash}')
    

with DAG (
    dag_id = 'mysql_hook_v3',
    description = 'connecting mysql to airflow using hook',
    start_date = datetime(2026,6,21),
    schedule = '0 0 * * *'
) as dag:
    task1 = PythonOperator(
        task_id = 'mysql_to_csv',
        python_callable = mysql_to_csv
    )
    task1