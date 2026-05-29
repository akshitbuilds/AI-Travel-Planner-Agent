import requests

def get_weather(latitude, longitude):

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m"

    response = requests.get(url)

    data = response.json()

    return data