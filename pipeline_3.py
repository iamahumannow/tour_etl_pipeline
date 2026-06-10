from extractors.flight_etl import extract_flight
from db_loader import load_hist_flight
from logger import get_logger
import pandas as pd

from logger import get_logger
logging = get_logger("pipeline_3", "pipeline_3.log")

arr_id = {'IXB':'Sikkim','TRV':'Varkala'}
dept_id = 'BOM'
outbound_date = '2026-11-19'
return_date = '2026-11-24'


def run():
    logging.info("Pipeline started.")
    for dest_id,dest in arr_id.items():
        try:
            df_flight = extract_flight(dept_id, dest_id,outbound_date,return_date,dest)
            df_final = pd.DataFrame(
                {'location':dest, 
                'price':df_flight['price'].mean()},
                index=[0]
                )
            df_final['price']=df_final['price'].round(2)
            load_hist_flight(df_final)
        except Exception as e:
            logging.error(f"Monthly flight pricing failed for {dest}: {e}")
    logging.info("Pipeline complete.\n")

if __name__ == "__main__":
    run()

