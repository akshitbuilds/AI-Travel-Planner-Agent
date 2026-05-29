"""
tools/hotel_tool.py
---------------------
LangChain tool for recommending hotels based on
city, budget per night, and rating preferences.
"""

from langchain.tools import tool
from utils.data_loader import load_hotels


@tool
def recommend_hotel(query: str) -> str:
    """
    Recommend the best hotels in a city based on budget and rating.
    Returns top-rated hotels within budget with justification.

    Input format: 'city budget_per_night' e.g. 'Goa 5000'
    """
    try:
        hotels = load_hotels()

        # Parse city and budget from query
        parts = query.strip().split()
        if len(parts) < 1:
            return "Please provide at least a city name."

        # Handle multi-word city names like "New Delhi"
        try:
            budget = int(parts[-1])
            city = " ".join(parts[:-1]).title()
        except ValueError:
            city = " ".join(parts).title()
            budget = 999999  # No budget limit if not specified

        # Filter by city
        city_hotels = [h for h in hotels if h["city"].lower() == city.lower()]
        if not city_hotels:
            return f"No hotels found in {city}. Available cities: Goa, Mumbai, Delhi, Jaipur, Shimla, Bangalore, Hyderabad, Chennai."

        # Filter by budget
        within_budget = [h for h in city_hotels if h["price_per_night"] <= budget]

        if not within_budget:
            # Suggest closest options if nothing in budget
            cheapest = sorted(city_hotels, key=lambda x: x["price_per_night"])[:2]
            result = f"No hotels found in {city} within ₹{budget}/night budget.\n"
            result += f"Closest available options:\n"
            for h in cheapest:
                result += f"  • {h['name']} – ₹{h['price_per_night']}/night ⭐{h['rating']}\n"
            return result

        # Sort by rating (highest first), then by price
        ranked = sorted(within_budget, key=lambda x: (-x["rating"], x["price_per_night"]))
        best = ranked[0]

        result = f"Hotels in {city} (budget: ₹{budget}/night):\n\n"
        result += f"🏨 RECOMMENDED (Best Rated Within Budget):\n"
        result += f"  Name: {best['name']}\n"
        result += f"  Price: ₹{best['price_per_night']}/night\n"
        result += f"  Rating: ⭐ {best['rating']}/5\n"
        result += f"  Type: {best['type']}\n"
        result += f"  Amenities: {', '.join(best['amenities'])}\n"
        result += f"  Reason: Highest rated ({best['rating']}) within your ₹{budget}/night budget.\n\n"

        result += f"Other options within budget ({len(within_budget)} total):\n"
        for h in ranked[1:3]:
            result += f"  • {h['name']} – ₹{h['price_per_night']}/night ⭐{h['rating']} ({h['type']})\n"

        return result

    except Exception as e:
        return f"Error fetching hotels: {str(e)}"