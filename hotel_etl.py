import serpapi
from dotenv import load_dotenv
import os
import json
import pandas as pd

def get_hotel_data(location, checkin_date, checkout_date, adults=1):
    load_dotenv()
    key = os.getenv("SERPAPI_KEY")
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
            print(f"SerpApi error: {results['error']}")
            return None
        return results['properties']
    except Exception as e:
        print(f"Error fetching hotel data: {e}")
        return None
    
def data_dump(raw_data):
    with open('hotel_data_raw.json', 'w') as f:
        json.dump(raw_data, f, indent=4)

def raw_data_cleaner(raw_data):
    df= pd.DataFrame(columns = ['name', 'stay_type', 'rating', 'price'])
    for hotel in raw_data:
        if 'total_rate' not in hotel:
            break
        try:
            name = hotel.get('name')
            stay_type= hotel['type']
            rating = hotel.get('location_rating')
            # price = hotel['total_rate']['extracted_lowest']
            price = hotel.get('total_rate', {}).get('extracted_lowest')
            noPeople=(item for item in hotel['essential_info'] if item.startswith('Sleeps'))
            Beds =(item for item in hotel['essential_info'] if 'beds' in item.lower())
            Bedroom =(item for item in hotel['essential_info'] if 'bedroom' in item.lower())
            Bathroom =(item for item in hotel['essential_info'] if 'bathroom' in item.lower())
            check_in_out = hotel['check_in_time'] + ' - ' + hotel['check_out_time']
            airport ='Yes' if any('airport' in place['name'].lower() for place in hotel.get('nearby_places', [])) else 'No'

            df2 = pd.DataFrame({
                'name': name,
                'stay_type': stay_type,
                'rating': rating,
                'price': price,
                'noPeople': next(noPeople, 'N/A').split()[-1],
                'Beds': next(Beds, 'N/A'),
                'Bedroom': next(Bedroom, 'N/A'),
                'Bathroom': next(Bathroom, 'N/A'),
                'check_in_out': check_in_out,
                'airport': airport
            }, index=[0])
        
            df = pd.concat([df, df2], ignore_index=True)
        except KeyError as e:
            print(f"KeyError: {e} in hotel data")
    return df



location = "Sikkim"
checkin_date = "2026-05-28"
checkout_date = "2026-06-03"

# raw_data = get_hotel_data(location, checkin_date, checkout_date, adults)
# data_dump(raw_data)

with open('hotel_data_raw.json', 'r') as f:
    raw_data = json.load(f)

df3= raw_data_cleaner(raw_data)
print(df3.head())
print(len(raw_data))
