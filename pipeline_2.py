import pandas as pd
from historical_weather_etl import hist_data
from pricing_etl import monthly_hotel_pricing, monthly_flight_pricing
from logger import get_logger

logging = get_logger("pipeline_2", "pipeline_2.log")

def compute_best_time(place,df_hist_weather,df_monthly_flight, df_monthly_hotel):
    logging.info(f"Computing best time to visit {place}")

    df_weather = df_hist_weather
    df_flight = df_monthly_flight
    df_hotel = df_monthly_hotel

    df_weather_score = df_weather.copy()
    df_weather_score['temperature_score'] = 1 - _norm(df_weather_score['temperature_2m'])
    df_weather_score['precipitation_score'] = 1 - _norm(df_weather_score['precipitation'])
    df_weather_score['sunshine_score'] = _norm(df_weather_score['sunshine_duration'])
    df_weather_score['low_temp_score'] = 1 -_norm(df_weather_score['temperature_2m_min'])

    df_weather_score['overall_weather_score'] = (
         df_weather_score['temperature_score'] *0.3+ 
         df_weather_score['precipitation_score'] *0.25+ 
         df_weather_score['sunshine_score'] *0.2+ 
         df_weather_score['low_temp_score'] *0.25)

    df_flight_score = df_flight.copy()
    df_flight_score['price_score'] = 1 - _norm(df_flight_score['price'])

    df_hotel_score = df_hotel.copy()
    df_hotel_score['price_score'] = 1 - _norm(df_hotel_score['price'])

    df_merged = pd.merge(
         df_weather_score[['months', 'overall_weather_score']], 
         df_flight_score[['months', 'price_score']], on='months', how='left')
    df_merged = pd.merge(
         df_merged, 
         df_hotel_score[['months', 'price_score']], on='months', how='left', suffixes=('_flight', '_hotel'))
    df_merged['price_score_flight'] = df_merged['price_score_flight'].fillna(0.5)
    df_merged['price_score_hotel'] = df_merged['price_score_hotel'].fillna(0.5)
    df_merged['overall_score'] = 0.55*df_merged['overall_weather_score'] + 0.23*df_merged['price_score_flight'] + 0.22*df_merged['price_score_hotel']
    df_merged = df_merged.round(2)
    df_merged.rename(columns={'overall_weather_score':'weather_score', 'price_score_flight': 'flight_price_score', 'price_score_hotel': 'hotel_price_score'}, inplace=True)
    df_merged['location'] = place
    logging.info(f"Best time computation completed for {place}")
    return df_merged


def _norm(series: pd.Series) -> pd.Series:
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([0.5] * len(series))
    return (series - min_val) / (max_val - min_val)
