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
    with open('hotel_pricing_data.json', 'w') as f:
        json.dump(raw_data, f, indent=4)

def monthly_flight(raw_data):
    df = pd.DataFrame(raw_data).T
    df.columns = ['lowest_price', 'price_level']
    df.index.name = 'Month'
    df.reset_index(inplace=True)
    df['Month'] = pd.to_datetime(df['Month'], format='%Y-%m-%d').dt.strftime('%B')
    return df

def monthly_hotel(raw_data):
    clean_data = {key: sum(value)/len(value) for key, value in raw_data.items()}
    df = pd.DataFrame(clean_data, index=['lowest_price']).T
    df.columns = ['lowest_price']
    df.index.name = 'Month'
    df.reset_index(inplace=True)
    df['Month'] = pd.to_datetime(df['Month'], format='%Y-%m-%d').dt.strftime('%B')
    df =df.round(2)
    return df

def get_hotel_data(location, checkin_date, checkout_date):
    load_dotenv()
    key = os.getenv("SERPAPI_KEY")
    try:
        client = serpapi.Client(api_key=key)
        results = client.search({
            'engine': "google_hotels",
            'q': location,
            'check_in_date': checkin_date,
            'check_out_date': checkout_date,
            'currency': "INR",
            })
        if 'error' in results:
            print(f"SerpApi error: {results['error']}")
            return None
        return results['properties']
    except Exception as e:
        print(f"Error fetching hotel data: {e}")
        return None

with open('hotel_data_raw.json', 'r') as f:
    raw_data = json.load(f)

location = 'Sikkim'
dept_id = 'BOM'
arr_id = 'IXB'
start_date = '2026-xx-08'
end_date = '2026-xx-14'
val={}
# res = get_hotel_data(location, start_date, end_date)
# data_dump(res)

# for x in range(pd.Timestamp.now().month+1,13):
#     checkin_date = start_date.replace('xx', str(x).zfill(2))
#     checkout_date = end_date.replace('xx', str(x).zfill(2))
#     val[checkin_date] = []
#     res =get_hotel_data(location, checkin_date, checkout_date)
#     for hotel in res:
#         if 'total_rate' not in hotel: break
#         val[checkin_date].append(hotel['total_rate']['extracted_lowest'])

# print(val)
# for hotel in raw_data:
#     price = hotel.get('total_rate', {}).get('extracted_lowest')
#     if price: print(price)

# val= {}

# for x in range(pd.Timestamp.now().month+1,13):
#     outbound_date = start_date.replace('xx', str(x).zfill(2))
#     return_date = end_date.replace('xx', str(x).zfill(2))
#     pricing_data = flight_price(dept_id, arr_id, outbound_date, return_date)
#     if pricing_data:
#         val[outbound_date] = [pricing_data['lowest_price'], pricing_data['price_level']]

# data_dump(val)

# df = monthly_flight(json.load(open('flight_pricing_data.json')))
# print(df)

df = monthly_hotel(json.load(open('hotel_pricing_data.json')))
print(df)