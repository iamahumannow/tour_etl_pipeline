import pandas as pd
from historical_weather_etl import hist_data
from pricing_etl import monthly_hotel_pricing, monthly_flight_pricing
from logger import get_logger

def compute_best_time(place):
    







def _norm(series: pd.Series) -> pd.Series:
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series([0.5] * len(series))
    return (series - min_val) / (max_val - min_val)