import serpapi
from dotenv import load_dotenv
import os
import json
import pandas as pd

def get_flight_data(dept_id, arr_id, outbound_date, return_date, adults=1):
    load_dotenv()
    key = os.getenv("SERPAPI_KEY")
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
            print(f"SerpApi error: {results['error']}")
            return None
        return results['best_flights']
    # except serpapi.SerpApiClientException as e:
    #     print(f"SerpApi error: {e}")
    #     return None
    except Exception as e:
        print(f"Error fetching flight data: {e}")
        return None
    
def data_dump(raw_data):
    with open('flight_data_raw.json', 'w') as f:
        json.dump(raw_data, f, indent=4)


def raw_data_cleaner(raw_data):
    x=0
    df = pd.DataFrame(columns = ['airline', 'airplane', 'departure_date', 'departure_time', 'arrival_date', 'arrival_time', 'duration', 'leg_room', 'price'])
    for flight in raw_data:
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
            print(f"Missing key {e} in flight data: {flight}")
            return df
    return df

dept_id = 'BOM'
arr_id = 'IXB'
outbound_date = '2026-05-28'
return_date = '2026-06-03'

# flight_data = get_flight_data(dept_id, arr_id, outbound_date, return_date, adults)
# if flight_data:
#     data_dump(flight_data)

with open('flight_data_raw.json', 'r') as f:
    raw_data = json.load(f)

df3 = raw_data_cleaner(raw_data)
print(df3.head())