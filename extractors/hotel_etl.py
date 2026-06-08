import re
import serpapi
from dotenv import load_dotenv
import os
import pandas as pd
from logger import get_logger
logging = get_logger("hotel_etl", "hotel_etl.log")


def get_hotel_data(location, checkin_date, checkout_date, adults=1):
    load_dotenv()
    key = os.getenv("SERPAPI_KEY")
    logging.info(f"Fetching hotel data for {location}...")
    try:
        client = serpapi.Client(api_key=key)
        results = client.search({
            'engine': "google_hotels",
            'q': location,
            'check_in_date': checkin_date,
            'check_out_date': checkout_date,
            'adults': adults,
            'currency': "INR",
            })
        if 'error' in results:
            logging.error(f"SerpApi error: {results['error']}")
            return None
        logging.info("Hotel data fetched successfully.")
        return results['properties']
    except Exception as e:
        logging.error(f"Error fetching hotel data: {e}")
        return None

def raw_data_cleaner(raw_data):
    df= pd.DataFrame(columns = ['name', 'stay_type', 'rating', 'price'])
    for hotel in raw_data:
        if 'total_rate' not in hotel:
            break
        try:
            name = hotel.get('name')
            stay_type= hotel['type']
            rating = hotel.get('location_rating')
            price = hotel.get('total_rate', {}).get('extracted_lowest')
            for item in hotel['essential_info']:
                if 'sleeps' in item.lower():
                    noPeople = item
                elif 'beds' in item.lower():
                    Beds = item
                elif 'bedroom' in item.lower():
                    Bedroom = item
                elif 'bathroom' in item.lower():
                    Bathroom = item
            check_in_out = hotel['check_in_time'] + ' - ' + hotel['check_out_time']
            airport =1 if any('airport' in place['name'].lower() for place in hotel.get('nearby_places', [])) else 0

            df2 = pd.DataFrame({
                'name': name,
                'stay_type': stay_type,
                'rating': rating,
                'price': price,
                'noPeople': int(x.group()) if (x := re.search(r'\d+$', noPeople)) else None,
                'Beds': int(x.group()) if (x := re.match(r'^\d+', Beds)) else None,
                'Bedroom': int(x.group()) if (x := re.match(r'^\d+', Bedroom)) else None,
                'Bathroom': int(x.group()) if (x := re.match(r'^\d+', Bathroom)) else None,
                'check_in_out': check_in_out,
                'airport': airport
            }, index=[0])
        
            df = pd.concat([df, df2], ignore_index=True)
        except KeyError as e:
            logging.error(f"Missing key in hotel data: {e} for hotel: {hotel.get('name', 'Unknown')}")
    logging.info(f"Extracted {len(df)} records.")
    logging.info(f"ETL complete. DataFrame shape: {df.shape}\n")
    return df





def extract_hotel(location, checkin_date, checkout_date):
    raw_data = get_hotel_data(location, checkin_date, checkout_date)
    df= raw_data_cleaner(raw_data)
    return df

# df = extract_hotel("Sikkim", "2026-06-28", "2026-07-03")
# print(df[['noPeople','Beds','Bedroom','Bathroom']])
# print(df[['noPeople','Beds','Bedroom','Bathroom']].dtypes)

# location = "Sikkim"
# checkin_date = "2026-06-28"
# checkout_date = "2026-07-03"

# data_dump(raw_data)
# with open('hotel_data_raw.json', 'r') as f:
#     raw_data = json.load(f)

# def data_dump(raw_data):
#     with open('hotel_data_raw.json', 'w') as f:
#         json.dump(raw_data, f, indent=4)

