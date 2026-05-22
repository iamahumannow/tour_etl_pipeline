import serpapi
from dotenv import load_dotenv
import os
import json
import pandas as pd



def flight_price(dept_id, arr_id, outbound_date, return_date):
    load_dotenv()
    api_key = os.getenv("SERPAPI_KEY")
    try:
        client = serpapi.Client(api_key = api_key)
        results = client.search({
            "engine": "google_flights",
            "departure_id": dept_id,
            "arrival_id": arr_id,
            "outbound_date": outbound_date,
            "return_date": return_date,
            'currency': 'INR'
        })
        if 'error' in results:
                print(f"SerpApi error: {results['error']}")
                return None
        return results['price_insights']

    except Exception as e:
        print(f"Error fetching flight data: {e}")
        return None

def data_dump(raw_data):
    with open('flight_pricing_data.json', 'w') as f:
        json.dump(raw_data, f, indent=4)

def monthly_flight(raw_data):
    df = pd.DataFrame(raw_data).T
    df.columns = ['lowest_price', 'price_level']
    df.index.name = 'Month'
    df.reset_index(inplace=True)
    df['Month'] = pd.to_datetime(df['Month'], format='%Y-%m-%d').dt.strftime('%B')
    return df

dept_id = 'BOM'
arr_id = 'IXB'
start_date = '2026-xx-08'
end_date = '2026-xx-14'


# val= {}

# for x in range(pd.Timestamp.now().month+1,13):
#     outbound_date = start_date.replace('xx', str(x).zfill(2))
#     return_date = end_date.replace('xx', str(x).zfill(2))
#     pricing_data = flight_price(dept_id, arr_id, outbound_date, return_date)
#     if pricing_data:
#         val[outbound_date] = [pricing_data['lowest_price'], pricing_data['price_level']]

# data_dump(val)

df = monthly_flight(json.load(open('flight_pricing_data.json')))
print(df)