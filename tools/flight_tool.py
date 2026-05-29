"""
tools/flight_tool.py
----------------------
LangChain tool for searching and recommending flights
from the local flights.json dataset.
"""

from langchain.tools import tool
from utils.data_loader import load_flights


@tool
def search_flights(query: str) -> str:
    """
    Search for available flights between two cities.
    Returns the cheapest and fastest options with reasoning.

    Input format: 'source to destination' e.g. 'Delhi to Goa'
    """
    try:
        flights = load_flights()

        # Parse source and destination from query string
        parts = query.lower().replace(" to ", "|").split("|")
        if len(parts) < 2:
            return "Invalid query. Please use format: 'City1 to City2'"

        source = parts[0].strip().title()
        destination = parts[1].strip().title()

        # Filter matching flights
        matching = [
            f for f in flights
            if f["source"].lower() == source.lower()
            and f["destination"].lower() == destination.lower()
        ]

        if not matching:
            return f"No direct flights found from {source} to {destination}. Consider nearby airports or stopovers."

        # Sort by price to find cheapest
        sorted_by_price = sorted(matching, key=lambda x: x["price"])
        cheapest = sorted_by_price[0]

        # Sort by duration to find fastest
        sorted_by_duration = sorted(matching, key=lambda x: x["duration"])
        fastest = sorted_by_duration[0]

        result = f"Flights from {source} to {destination}:\n\n"
        result += f"✈ RECOMMENDED (Cheapest):\n"
        result += f"  Airline: {cheapest['airline']}\n"
        result += f"  Price: ₹{cheapest['price']}\n"
        result += f"  Duration: {cheapest['duration']}\n"
        result += f"  Departure: {cheapest['departure']} → Arrival: {cheapest['arrival']}\n"
        result += f"  Class: {cheapest['class']}\n"
        result += f"  Reason: Lowest price among {len(matching)} available options.\n\n"

        if fastest["airline"] != cheapest["airline"]:
            result += f"⚡ Fastest Option:\n"
            result += f"  Airline: {fastest['airline']}, Price: ₹{fastest['price']}, Duration: {fastest['duration']}\n"

        result += f"\nTotal options available: {len(matching)}"
        return result

    except Exception as e:
        return f"Error fetching flights: {str(e)}"