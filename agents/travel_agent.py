from tools.flight_tool import get_flights
from tools.hotel_tool import get_hotels
from tools.places_tool import get_places
from tools.budget_tool import calculate_budget
from tools.weather_tool import get_weather


def generate_trip(source, destination, days, budget):

    flights = get_flights(source, destination)

    hotels = get_hotels(destination, budget)

    places = get_places(destination)

    selected_flight = flights[0]

    selected_hotel = hotels[0]

    weather = get_weather(15.2993, 74.1240)

    temperature = weather["current"]["temperature_2m"]

    total_budget = calculate_budget(
        selected_flight["price"],
        selected_hotel["price_per_night"] * days,
        days
    )

    return {
        "destination": destination,

        "flight": selected_flight,

        "hotel": selected_hotel,

        "temperature": temperature,

        "places": places,

        "budget": total_budget
    }