import requests
import pandas as pd
from geopy.geocoders import Nominatim

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

# res = extract_weather_data(location={"latitude": 27.3257, "longitude": -88.6122})
    
# print(res)
x=input("Enter the location: ")
location = get_location(x)
if location:
    weather_data = extract_weather_data(location)
    if weather_data:
        print(weather_data)

