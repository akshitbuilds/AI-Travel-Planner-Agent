"""
tools/budget_tool.py
----------------------
LangChain tool for estimating total trip budget
including flights, hotels, food, transport, and activities.
"""

from langchain.tools import tool
from utils.data_loader import load_flights, load_hotels


@tool
def estimate_budget(query: str) -> str:
    """
    Estimate total trip cost including flights, hotel, food, transport, and activities.
    Provides a detailed cost breakdown with optimization tips.

    Input format: 'source destination days hotel_budget_per_night'
    Example: 'Delhi Goa 3 5000'
    """
    try:
        parts = query.strip().split()
        if len(parts) < 3:
            return "Please provide: source destination days (and optionally hotel_budget)"

        source = parts[0].title()
        destination = parts[1].title()
        days = int(parts[2])
        hotel_budget = int(parts[3]) if len(parts) > 3 else 5000

        flights = load_flights()
        hotels = load_hotels()

        # Find cheapest flight
        matching_flights = [
            f for f in flights
            if f["source"].lower() == source.lower()
            and f["destination"].lower() == destination.lower()
        ]
        if matching_flights:
            cheapest_flight = sorted(matching_flights, key=lambda x: x["price"])[0]
            flight_cost = cheapest_flight["price"]
            flight_note = f"{cheapest_flight['airline']} – cheapest available"
        else:
            flight_cost = 4500  # Default estimate
            flight_note = "Estimated (no direct flight data)"

        # Find best hotel within budget
        matching_hotels = [
            h for h in hotels
            if h["city"].lower() == destination.lower()
            and h["price_per_night"] <= hotel_budget
        ]
        if matching_hotels:
            best_hotel = sorted(matching_hotels, key=lambda x: -x["rating"])[0]
            hotel_per_night = best_hotel["price_per_night"]
            hotel_total = hotel_per_night * days
            hotel_note = f"{best_hotel['name']} ⭐{best_hotel['rating']}"
        else:
            hotel_per_night = hotel_budget
            hotel_total = hotel_budget * days
            hotel_note = "Based on your budget input"

        # Standard estimates per day
        food_per_day = 800
        transport_per_day = 600
        activities_per_day = 400

        food_total = food_per_day * days
        transport_total = transport_per_day * days
        activities_total = activities_per_day * days

        grand_total = flight_cost + hotel_total + food_total + transport_total + activities_total

        result = f"Budget Breakdown for {days}-Day Trip: {source} → {destination}\n"
        result += "=" * 50 + "\n\n"
        result += f"  ✈  Flight:      ₹{flight_cost:,}   ({flight_note})\n"
        result += f"  🏨 Hotel:       ₹{hotel_total:,}   ({hotel_note}, ₹{hotel_per_night}/night × {days} nights)\n"
        result += f"  🍽  Food:        ₹{food_total:,}   (₹{food_per_day}/day × {days} days)\n"
        result += f"  🚕 Transport:   ₹{transport_total:,}   (₹{transport_per_day}/day × {days} days)\n"
        result += f"  🎟  Activities:  ₹{activities_total:,}   (₹{activities_per_day}/day × {days} days)\n"
        result += "-" * 50 + "\n"
        result += f"  💰 TOTAL:       ₹{grand_total:,}\n\n"
        result += f"Tips to save:\n"
        result += f"  • Book flights 2–3 weeks in advance\n"
        result += f"  • Use local transport (auto/bus) instead of taxis\n"
        result += f"  • Choose budget hotels if ₹{hotel_per_night} feels high\n"

        return result

    except Exception as e:
        return f"Error estimating budget: {str(e)}"