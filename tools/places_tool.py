"""
tools/places_tool.py
----------------------
LangChain tool for discovering top tourist places,
attractions, and POIs in a destination city.
"""

from langchain.tools import tool
from utils.data_loader import load_places


@tool
def find_places(city: str) -> str:
    """
    Find and rank top tourist attractions and places of interest in a city.
    Returns top-rated places with entry fees, best visit times, and descriptions.

    Input: City name e.g. 'Goa' or 'Jaipur'
    """
    try:
        places = load_places()

        city_places = [p for p in places if p["city"].lower() == city.strip().lower()]

        if not city_places:
            return (
                f"No places found for {city}. "
                f"Available cities: Goa, Mumbai, Jaipur, Shimla, Bangalore, Hyderabad, Chennai, Kolkata."
            )

        # Sort by rating descending
        ranked = sorted(city_places, key=lambda x: x["rating"], reverse=True)
        top = ranked[:8]  # Return top 8 places

        result = f"Top tourist attractions in {city}:\n\n"
        for i, place in enumerate(top, 1):
            fee = f"₹{place['entry_fee']}" if place["entry_fee"] > 0 else "Free"
            result += (
                f"{i}. {place['name']}\n"
                f"   Type: {place['type']} | Rating: ⭐{place['rating']} | Entry: {fee}\n"
                f"   Best time: {place['best_time']}\n"
                f"   About: {place['description']}\n\n"
            )

        return result

    except Exception as e:
        return f"Error fetching places: {str(e)}"