"""
utils/weather_utils.py
-----------------------
Utility module for fetching real-time weather forecasts
using the free Open-Meteo API (no API key required).
"""

import requests

# Geocoding data for major Indian cities
CITY_COORDINATES = {
    "goa": {"latitude": 15.2993, "longitude": 74.1240},
    "mumbai": {"latitude": 19.0760, "longitude": 72.8777},
    "delhi": {"latitude": 28.7041, "longitude": 77.1025},
    "jaipur": {"latitude": 26.9124, "longitude": 75.7873},
    "bangalore": {"latitude": 12.9716, "longitude": 77.5946},
    "shimla": {"latitude": 31.1048, "longitude": 77.1734},
    "hyderabad": {"latitude": 17.3850, "longitude": 78.4867},
    "chennai": {"latitude": 13.0827, "longitude": 80.2707},
    "kolkata": {"latitude": 22.5726, "longitude": 88.3639},
    "agra": {"latitude": 27.1767, "longitude": 78.0081},
    "varanasi": {"latitude": 25.3176, "longitude": 82.9739},
    "udaipur": {"latitude": 24.5854, "longitude": 73.7125},
    "manali": {"latitude": 32.2396, "longitude": 77.1887},
    "kerala": {"latitude": 10.8505, "longitude": 76.2711},
    "ooty": {"latitude": 11.4102, "longitude": 76.6950},
    "darjeeling": {"latitude": 27.0410, "longitude": 88.2663},
    "pune": {"latitude": 18.5204, "longitude": 73.8567},
    "ahmedabad": {"latitude": 23.0225, "longitude": 72.5714},
}


def get_weather_description(temp: float, wmo_code: int = None) -> str:
    """
    Convert temperature and WMO weather code to a human-readable description.

    Args:
        temp: Temperature in Celsius
        wmo_code: WMO weather interpretation code (optional)

    Returns:
        A descriptive string like 'Sunny (31°C)'
    """
    wmo_descriptions = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Heavy drizzle", 61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Light snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight showers", 81: "Moderate showers", 82: "Heavy showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail",
    }
    condition = wmo_descriptions.get(wmo_code, "Sunny") if wmo_code is not None else _temp_to_condition(temp)
    return f"{condition} ({temp:.0f}°C)"


def _temp_to_condition(temp: float) -> str:
    """Fallback: derive weather condition from temperature."""
    if temp >= 35:
        return "Hot & Sunny"
    elif temp >= 28:
        return "Sunny"
    elif temp >= 22:
        return "Partly Cloudy"
    elif temp >= 15:
        return "Mild & Cloudy"
    else:
        return "Cool & Cloudy"


def get_city_coordinates(city: str) -> dict | None:
    """
    Look up coordinates for a given city name.

    Args:
        city: City name string

    Returns:
        Dict with latitude/longitude or None if not found
    """
    return CITY_COORDINATES.get(city.lower().strip())


def fetch_weather_forecast(city: str, days: int = 3) -> list[dict]:
    """
    Fetch day-wise weather forecast from Open-Meteo API.

    Args:
        city: Destination city name
        days: Number of forecast days (1–7)

    Returns:
        List of dicts: [{"day": 1, "date": "...", "description": "Sunny (31°C)", "temp": 31}]
    """
    coords = get_city_coordinates(city)
    if not coords:
        # Return placeholder data if city not in our list
        return [
            {"day": i + 1, "date": f"Day {i + 1}", "description": f"Sunny (30°C)", "temp": 30}
            for i in range(days)
        ]

    days_clamped = min(max(days, 1), 7)
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={coords['latitude']}&longitude={coords['longitude']}"
        f"&daily=temperature_2m_max,weathercode"
        f"&timezone=Asia/Kolkata"
        f"&forecast_days={days_clamped}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        temps = daily.get("temperature_2m_max", [])
        codes = daily.get("weathercode", [])

        forecast = []
        for i in range(min(days_clamped, len(dates))):
            forecast.append({
                "day": i + 1,
                "date": dates[i],
                "description": get_weather_description(temps[i], codes[i]),
                "temp": round(temps[i], 1),
            })
        return forecast

    except (requests.RequestException, KeyError, ValueError) as e:
        # Graceful fallback on API failure
        return [
            {"day": i + 1, "date": f"Day {i + 1}", "description": "Sunny (30°C)", "temp": 30}
            for i in range(days)
        ]