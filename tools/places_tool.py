import json

def get_places(city):

    with open("data/places.json", "r") as file:
        places = json.load(file)

    recommendations = []

    for place in places:

        if place["city"].lower() == city.lower():

            recommendations.append(place)

    recommendations = sorted(
        recommendations,
        key=lambda x: x["rating"],
        reverse=True
    )

    return recommendations[:5]