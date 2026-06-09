import requests
import pandas as pd
from geopy.geocoders import Nominatim
from logger import get_logger
logging = get_logger("historical_weather_etl", "historical_weather_etl.log")

def get_location(val):
    locator = Nominatim(user_agent="mygeocoder")
    location = locator.geocode(val)
    if location:
        location = {"name": location.address, "latitude": location.latitude, "longitude": location.longitude}
    else:    
        logging.error("Location not found")
    return location


def extract_weather_data(location):
    url = "https://archive-api.open-meteo.com/v1/archive"
    logging.info(f"Extracting weather data for {location['name']}")
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        'start_date': '2025-01-01',
        'end_date': '2025-12-31',
        "daily" : "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_hours,sunshine_duration",
        'timezone': "auto",
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logging.info(f"Weather data extracted successfully for {location['name']}")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while fetching: {e}")
        return None

def raw_data_cleaner(raw_data,location):
    logging.info(f"Cleaning weather data for {location}")
    try:
        latitude = raw_data['latitude']
        longitude = raw_data['longitude']
        daily_time = pd.to_datetime(raw_data['daily']['time'])
        daily_temp2m_mean = raw_data['daily']['temperature_2m_mean']
        daily_temp2m_max = raw_data['daily']['temperature_2m_max']
        daily_temp2m_min = raw_data['daily']['temperature_2m_min']
        daily_precipitation_hours = raw_data['daily']['precipitation_hours']
        daily_sunshine_duration = raw_data['daily']['sunshine_duration']        
        
        df = pd.DataFrame({
            'latitude': latitude,
            'longitude': longitude,
            'months': daily_time,
            'temperature_2m': daily_temp2m_mean,
            'temperature_2m_max': daily_temp2m_max,
            'temperature_2m_min': daily_temp2m_min,
            'precipitation': daily_precipitation_hours,
            'sunshine_duration': daily_sunshine_duration
        })

        df = df.set_index('months').resample('ME').mean(numeric_only=True).reset_index()
        df['location'] = location
        df['months']=df['months'].dt.month_name()
        df['sunshine_duration'] = df['sunshine_duration']/3600
        df = df.round(2)
        logging.info(f"Cleaning completed successfully for {location}")
        return df

    except KeyError as e:
        logging.error(f"API structure changed, Missing key: {e}")
        return None

def hist_data(place):
    location = get_location(place)
    if location:
        raw_data = extract_weather_data(location)
        if raw_data:
            return raw_data_cleaner(raw_data, place)
    logging.error(f"Failed to get historical weather data for {place}")
    return None

#print(hist_data('Sikkim'))

# def data_dump(raw_data):
#     with open('historical_weather_data_raw.json', 'w') as f:
#         json.dump(raw_data, f, indent=4)

# with open('historical_weather_data_raw.json', 'r') as f:
#     raw_data = json.load(f)