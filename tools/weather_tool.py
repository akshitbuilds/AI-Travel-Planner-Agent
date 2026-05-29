"""
tools/weather_tool.py
-----------------------
LangChain tool for fetching real-time weather forecasts
using the free Open-Meteo API (no API key required).
"""

from langchain.tools import tool
from utils.weather_utils import fetch_weather_forecast


@tool
def get_weather(query: str) -> str:
    """
    Get day-wise real-time weather forecast for a travel destination.
    Uses the free Open-Meteo API — no API key needed.

    Input format: 'city days' e.g. 'Goa 3' or just 'Goa'
    """
    try:
        parts = query.strip().split()
        city = parts[0].title()
        days = int(parts[1]) if len(parts) > 1 else 3
        days = min(max(days, 1), 7)

        forecast = fetch_weather_forecast(city, days)

        result = f"Weather forecast for {city} ({days} days):\n\n"
        for day in forecast:
            result += f"  Day {day['day']} ({day['date']}): {day['description']}\n"

        result += "\nSource: Open-Meteo API (live data)"
        return result

    except Exception as e:
        return f"Error fetching weather: {str(e)}"