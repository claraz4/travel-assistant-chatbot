# tools/city_weather.py

import json
from pathlib import Path
from langchain.tools import tool

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CITY_WEATHER_PATH = PROJECT_ROOT / "json" / "city_weather.json"

# Load weather data
try:
    with open(CITY_WEATHER_PATH, "r", encoding="utf-8") as f:
        CITY_WEATHER = json.load(f)
except:
    CITY_WEATHER = {}


@tool
def get_city_monthly_weather(city: str, month: str) -> str:
    """
    Retrieve typical weather for a city in a specific month.
    City examples: 'Paris', 'Beirut', 'Dubai'.
    Month: any of the 12 months.
    """
    if not CITY_WEATHER:
        return "City weather data is not loaded. Check city_weather.json."

    city_key = city.strip().lower()
    month_key = month.strip().lower()

    if city_key not in CITY_WEATHER:
        available = ", ".join(CITY_WEATHER.keys())
        return f"No data for {city}. Available cities: {available}."

    city_data = CITY_WEATHER[city_key]

    if month_key not in city_data:
        available_months = ", ".join(city_data.keys())
        return f"No weather info for {month} in {city}. Available months: {available_months}."

    return f"Weather in {city.title()} in {month.title()}: {city_data[month_key]}"
