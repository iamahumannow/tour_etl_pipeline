import serpapi
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from logger import get_logger
logging = get_logger("pricing_etl", "pricing_etl.log")

def flight_price(dept_id, arr_id, outbound_date, return_date,adults=1):
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
            'currency': 'INR',
            'adults': adults
        })
        if 'error' in results:
                logging.error(f"SerpApi error: {results['error']}")
                return None
        return results['price_insights']

    except Exception as e:
        logging.error(f"Error fetching flight data: {e}")
        return None

def monthly_flight(raw_data,location):
    df = pd.DataFrame(raw_data).T
    df.columns = ['lowest_price', 'price_level']
    df.index.name = 'Month'
    df.reset_index(inplace=True)
    df['Month'] = pd.to_datetime(df['Month'], format='%Y-%m-%d').dt.strftime('%B')
    df = df.round(2)
    df['Location'] = location
    df.insert(0, 'Location', df.pop('Location'))
    return df

def monthly_hotel(raw_data, location):
    clean_data = {key: sum(value)/len(value) for key, value in raw_data.items()}
    df = pd.DataFrame(clean_data, index=['lowest_price']).T
    df.columns = ['lowest_price']
    df.index.name = 'Month'
    df.reset_index(inplace=True)
    df['Month'] = pd.to_datetime(df['Month'], format='%Y-%m-%d').dt.strftime('%B')
    df =df.round(2)
    df['Location'] = location
    df.insert(0, 'Location', df.pop('Location'))
    return df

def get_hotel_data(location, checkin_date, checkout_date,adults=1):
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
            'adults': adults
            })
        if 'error' in results:
            logging.error(f"SerpApi error: {results['error']}")
            return None
        return results['properties']
    except Exception as e:
        logging.error(f"Error fetching hotel data: {e}")
        return None

location = 'Sikkim'
dept_id = 'BOM'
arr_id = 'IXB'
start_date = datetime.today()
end_date = start_date + relativedelta(days=7)
val={}

for i in range(10):
    checkin_date = (start_date + relativedelta(months=i)).strftime('%Y-%m-%d')
    checkout_date = (end_date + relativedelta(months=i)).strftime('%Y-%m-%d')
    val[checkin_date] = []
    res =get_hotel_data(location, checkin_date, checkout_date)
    for hotel in res:
        if 'total_rate' not in hotel: break
        val[checkin_date].append(hotel['total_rate']['extracted_lowest'])

print(monthly_hotel(val,location))

for x in range(10):
    outbound_date = (start_date + relativedelta(months=x)).strftime('%Y-%m-%d')
    return_date = (end_date + relativedelta(months=x)).strftime('%Y-%m-%d')
    pricing_data = flight_price(dept_id, arr_id, outbound_date, return_date)
    if pricing_data:
        val[outbound_date] = [pricing_data['lowest_price'], pricing_data['price_level']]
    else:
        logging.warning(f"No flight data available for {outbound_date}")
        val[outbound_date] = [None, None]

print(monthly_flight(val,location))
# for x in range(pd.Timestamp.now().month+1,13):
#     outbound_date = start_date.replace('xx', str(x).zfill(2))
#     return_date = end_date.replace('xx', str(x).zfill(2))
#     pricing_data = flight_price(dept_id, arr_id, outbound_date, return_date)
#     if pricing_data:
#         val[outbound_date] = [pricing_data['lowest_price'], pricing_data['price_level']]


#with open('hotel_data_raw.json', 'r') as f:
#     raw_data = json.load(f)

# def data_dump(raw_data):
#     with open('hotel_pricing_data.json', 'w') as f:
#         json.dump(raw_data, f, indent=4)