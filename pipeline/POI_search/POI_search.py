from amadeus import Client, ResponseError
from dotenv import dotenv_values
from airportsdata import load

import subprocess
import requests
import amadeus
import json
import os

credentials = dict(dotenv_values("/Users/oluwaseyi/Documents/repositories/myvacaypal/.env"))

airports = load("IATA")
PATH = "../entity_extraction/entity_extraction_output/entities.json"
OUTPUT_PATH = "flight_search_output/flight.json"
amadeus = Client(
    client_id=credentials['API_KEY'],
    client_secret=credentials['API_SECRET']
)

def get_iata_code_by_city(city_name):
    for code, info in airports.items():
        if city_name.lower() in info['city'].lower():
            return code
    return None


def search_POIs():
    headers = {
        "Authorization": f"Bearer {credentials['ACCESS_TOKEN']}"
        }
    params = {
        "latitude":41.4036,
        "longitude":2.1744
    }
    response = requests.get(credentials["POI_SEARCH_URL"], headers=headers, params=params)
    return response.json()


if __name__ == "__main__":
    print(search_POIs())