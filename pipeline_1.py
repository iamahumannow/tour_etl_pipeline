from extractors.weather_etl   import extract_weather
from extractors.flight_etl   import extract_flight
from extractors.hotel_etl    import extract_hotel
from historical_weather_etl import hist_data
from pricing_etl import monthly_hotel_pricing, monthly_flight_pricing
from pipeline_2 import compute_best_time

from db_loader import load_weather, load_flight, load_hotel, load_monthly_weather, load_monthly_flight, load_monthly_hotel, load_best_time

from logger import get_logger
logging = get_logger("pipeline_1", "pipeline_1.log")

start_date = '2026-06-28'
end_date = '2026-07-03'
arr_id = 'IXB'
dept_id = 'BOM'

destinations = ['Sikkim']

def run():
    logging.info("Pipeline started.")
    for place in destinations:
        try:
            df_weather = extract_weather(place)  
            load_weather(df_weather)
        except Exception as e:
            logging.error(f"Weather failed for {place}: {e}")

        try:
            df_flights = extract_flight(dept_id, arr_id, start_date, end_date, location=place)
            load_flight(df_flights)
        except Exception as e:
            logging.error(f"Flights failed for {place}: {e}")

        try:
            df_hotels = extract_hotel(place, start_date, end_date)
            load_hotel(df_hotels)
        except Exception as e:
            logging.error(f"Hotels failed for {place}: {e}")
        
        try:
            df_hist_weather = hist_data(place)
            load_monthly_weather(df_hist_weather)
        except Exception as e:
            logging.error(f"Historical weather failed for {place}: {e}")
        
        try:
            df_monthly_flight = monthly_flight_pricing(dept_id, arr_id)
            load_monthly_flight(df_monthly_flight)
        except Exception as e:
            logging.error(f"Monthly flight pricing failed for {place}: {e}")

        try:
            df_monthly_hotel = monthly_hotel_pricing(place)
            load_monthly_hotel(df_monthly_hotel)
        except Exception as e:
            logging.error(f"Monthly hotel pricing failed for {place}: {e}")
        try:
            df_best_time = compute_best_time(place,df_hist_weather,df_monthly_flight, df_monthly_hotel)
            load_best_time(df_best_time)
        except Exception as e:
            logging.error(f"Best time computation failed for {place}: {e}")

    logging.info("Pipeline complete.\n")


if __name__ == "__main__":
    run()