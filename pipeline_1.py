from extractors.weather_etl   import extract_weather
from extractors.flight_etl   import extract_flight
from extractors.hotel_etl    import extract_hotel

from db_loader import load_weather, load_flight, load_hotel

from logger import get_logger
logging = get_logger("pipeline_1", "pipeline_1.log")

place = 'Sikkim'
start_date = '2026-06-28'
end_date = '2026-07-03'
arr_id = 'IXB'
dept_id = 'BOM'

def run():
    logging.info("Pipeline started.")

    try:
        df_weather = extract_weather(place)  
        load_weather(df_weather)
    except Exception as e:
        logging.error(f"Weather failed for {place}: {e}")

    try:
        df_flights = extract_flight(dept_id, arr_id, start_date, end_date)
        load_flight(df_flights)
    except Exception as e:
        logging.error(f"Flights failed for {place}: {e}")

    try:
        df_hotels = extract_hotel(place, start_date, end_date)
        load_hotel(df_hotels)
    except Exception as e:
        logging.error(f"Hotels failed for {place}: {e}")

    logging.info("Pipeline complete.\n")


if __name__ == "__main__":
    run()