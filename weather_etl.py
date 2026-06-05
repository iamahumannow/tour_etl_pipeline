import requests
import pandas as pd
from geopy.geocoders import Nominatim
import json

def get_location(val):
    locator = Nominatim(user_agent="mygeocoder")
    location = locator.geocode(val)

    if location:
        location = {"name": location.address, "latitude": location.latitude, "longitude": location.longitude}
    else:    
        print("Location not found")
    return location

def extract_weather_data(location):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": "temperature_2m,precipitation",
        "daily": "sunshine_duration",
        "current":'precipitation,temperature_2m',
        'timezone': "auto",
        'past_days': 14,
        'forecast_days': 14
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching: {e}")
        return None


def data_dump(raw_data):
    with open('weather_data_raw.json', 'w') as f:
        json.dump(raw_data, f, indent=4)

def raw_data_cleaner(raw_data):
    try:
        latitude = raw_data['latitude']
        longitude = raw_data['longitude']
        elevation = raw_data['elevation']
        hourwise = raw_data['hourly']['time']
        hourwise_temp2m = raw_data['hourly']['temperature_2m']
        hourwise_precipitation = raw_data['hourly']['precipitation']
        sunshine_duration = raw_data['daily']['sunshine_duration']
        
        df = pd.DataFrame({
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation,
            'date': pd.to_datetime(hourwise).date,
            'time': pd.to_datetime(hourwise).time,
            'temperature_2m': hourwise_temp2m,
            'precipitation': hourwise_precipitation,
            'sunshine_duration': sunshine_duration
        })
        df['sunshine_duration'] = df['sunshine_duration']/3600

        return df

    except KeyError as e:
        print(f"API structure changed, Missing key: {e}")
        return None
# res = extract_weather_data(location={"latitude": 27.3257, "longitude": -88.6122})
# print(res)

#x=input("Enter the location: ")

#location = get_location(x)
#raw_data = extract_weather_data(location)
#data_dump(raw_data)

# if location:
#     weather_data = extract_weather_data(location)
#     if weather_data:
#         print(weather_data)

with open('Tour_etl_pipeline/weather_data_raw.json', 'r') as f:
    raw_data = json.load(f)

df = raw_data_cleaner(raw_data)
print(df.head())

