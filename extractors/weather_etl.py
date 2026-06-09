import requests
import pandas as pd
from geopy.geocoders import Nominatim
import json
from logger import get_logger
logging = get_logger("weather_etl", "weather_etl.log")

def get_location(val):
    locator = Nominatim(user_agent="mygeocoder")
    location = locator.geocode(val)

    if location:
        location = {"name": location.address, "latitude": location.latitude, "longitude": location.longitude}
    else:    
        logging.error("Location not found")
    return location

def extract_weather_data(location):
    logging.info(f"Fetching weather data for location: {location['name']}")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": "temperature_2m,precipitation",
        "current":'precipitation,temperature_2m',
        'timezone': "auto",
        'past_days': 14,
        'forecast_days': 14
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Weather data fetched successfully for {location['name']}")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while fetching: {e}")
        return None

def raw_data_cleaner(raw_data,x):
    try:
        latitude = raw_data['latitude']
        longitude = raw_data['longitude']
        elevation = raw_data['elevation']
        hourwise = raw_data['hourly']['time']
        hourwise_temp2m = raw_data['hourly']['temperature_2m']
        hourwise_precipitation = raw_data['hourly']['precipitation']
        
        df = pd.DataFrame({
            'location': x,
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation,
            'hour_date': pd.to_datetime(hourwise).date,
            'hour_time': pd.to_datetime(hourwise).time,
            'hour_temp': hourwise_temp2m,
            'hour_precipitation': hourwise_precipitation,
        })
        df['latitude'] = df['latitude'].round(2)
        df['longitude'] = df['longitude'].round(2)
        logging.info(f"Extracted {len(df)} records.")
        logging.info(f"ETL complete. DataFrame shape: {df.shape}\n")
        return df

    except KeyError as e:
        logging.error(f"API structure changed, Missing key: {e}")
        return None


def extract_weather(x):
    location = get_location(x)
    raw_data = extract_weather_data(location)
    df = raw_data_cleaner(raw_data,x)
    return df



#x=input("Enter the location: ")
# print(df.head())
#data_dump(raw_data)

# if location:
#     weather_data = extract_weather_data(location)
#     if weather_data:
#         print(weather_data)

# with open('Tour_etl_pipeline/weather_data_raw.json', 'r') as f:
#     raw_data = json.load(f)

# def data_dump(raw_data):
#     with open('weather_data_raw.json', 'w') as f:
#         json.dump(raw_data, f, indent=4)
