import json

def get_hotels(city, budget):

    with open("data/hotels.json", "r") as file:
        hotels = json.load(file)

    filtered = []

    for hotel in hotels:

        if (
            hotel["city"].lower() == city.lower()
            and hotel["price_per_night"] <= budget
        ):

            filtered.append(hotel)

    filtered = sorted(
        filtered,
        key=lambda x: x["rating"],
        reverse=True
    )

    return filtered[:3]