import json

def get_flights(source, destination):

    with open("data/flights.json", "r") as file:
        flights = json.load(file)

    results = []

    for flight in flights:

        if (
            flight["source"].lower() == source.lower()
            and flight["destination"].lower() == destination.lower()
        ):

            results.append(flight)

    results = sorted(results, key=lambda x: x["price"])

    return results[:3]