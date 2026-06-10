import serpapi
from dotenv import load_dotenv
import os
import pandas as pd
from logger import get_logger

logging = get_logger("flight_etl", "flight_etl.log")

def get_flight_data(dept_id, arr_id, outbound_date, return_date, adults=1):
    load_dotenv()
    key = os.getenv("SERPAPI_KEY")
    logging.info("Fetching flight data...")
    try:
        client = serpapi.Client(api_key=key)
        results = client.search({
            'engine': "google_flights",
            'departure_id': dept_id,
            'arrival_id': arr_id,
            'currency': "INR",
            'outbound_date': outbound_date,
            'return_date': return_date,
            'adults': adults,
            'stops' : 1
            })
        if 'error' in results:
            logging.error(f"SerpApi error: {results['error']}")
            return None
        logging.info("Flight data fetched successfully.")
        return results['other_flights']
    except Exception as e:
        logging.error(f"Error fetching flight data: {e}")
        return None


def raw_data_cleaner(raw_data,location):
    df = pd.DataFrame(columns = ['airline', 'airplane', 'departure_date', 'departure_time', 'arrival_date', 'arrival_time', 'duration', 'leg_room', 'price'])
    for flight in raw_data:
        if 'price' not in flight: break
        try:
            airline = flight['flights'][0].get('airline')
            flight_number = flight['flights'][0].get('flight_number')
            airplane = flight['flights'][0].get('airplane')
            departure_time = flight['flights'][0].get('departure_airport', {}).get('time')
            arrival_time = flight['flights'][0].get('arrival_airport', {}).get('time')
            duration = flight.get('total_duration')
            leg_room = flight['flights'][0].get('legroom')
            price = flight.get('price')

            df2 = pd.DataFrame({
                'location': location,
                'airline': airline,
                'flight_number': flight_number,
                'airplane': airplane,
                'departure_date': departure_time.split(' ')[0],
                'departure_time': departure_time.split(' ')[1],
                'arrival_date': arrival_time.split(' ')[0],
                'arrival_time': arrival_time.split(' ')[1],
                'duration': duration,
                'leg_room': leg_room,
                'price': price
            }, index=[0])

            df = pd.concat([df, df2], ignore_index=True)

        except KeyError as e:
            logging.error(f"Missing key {e} in flight data: {flight}")
            return df
    logging.info(f"Extracted {len(df)} records.")
    logging.info(f"ETL complete. DataFrame shape: {df.shape}\n")
    return df

def extract_flight(dept_id, arr_id, outbound_date, return_date, location):
    raw_data = get_flight_data(dept_id, arr_id, outbound_date, return_date)
    df = raw_data_cleaner(raw_data, location)
    return df
