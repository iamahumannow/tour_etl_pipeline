from datetime import datetime
from io import BytesIO
from airflow import DAG
from airflow.decorators import task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd

BUCKET_NAME = "airflow-bucket"
CONN_ID = "minio_conn"  # The Connection ID you created in Step 2

with DAG(
    dag_id="dataframe_s3_hook_sharing",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False
) as dag:

    @task
    def generate_and_upload_df():
        df = pd.DataFrame({"user_id": [101, 102, 103], "score": [95, 88, 92]})
        
        # Convert DataFrame to Parquet bytes
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, index=False)
        parquet_buffer.seek(0)
        
        object_name = f"stage/scores_{datetime.now().strftime('%Y%m%d%H%M%S')}.parquet"
        
        # Initialize S3Hook pointing to MinIO connection
        s3_hook = S3Hook(aws_conn_id=CONN_ID)
        
        # Load the memory buffer directly to MinIO/S3
        s3_hook.load_file_obj(
            file_obj=parquet_buffer,
            key=object_name,
            bucket_name=BUCKET_NAME,
            replace=True
        )
        
        return object_name

    @task
    def download_and_process_df(object_name: str):
        s3_hook = S3Hook(aws_conn_id=CONN_ID)
        
        # Download the file object straight into memory
        s3_obj = s3_hook.get_key(key=object_name, bucket_name=BUCKET_NAME)
        file_bytes = s3_obj.get()["Body"].read()
        
        # Read back into pandas
        df = pd.read_parquet(BytesIO(file_bytes))
        
        print("Data successfully retrieved via S3Hook:")
        print(df.head())

    # DAG Dependency
    file_key = generate_and_upload_df()
    download_and_process_df(file_key)