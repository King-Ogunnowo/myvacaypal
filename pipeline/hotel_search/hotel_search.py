from amadeus import Client, ResponseError
from dotenv import dotenv_values
from airportsdata import load

import subprocess
import requests
import amadeus
import json
import os


creds = dotenv_values("/Users/oluwaseyi/Documents/repositories/myvacaypal/.env")

airports = load("IATA")
PATH = "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/entity_extraction/entity_extraction_output/entities.json"
OUTPUT_PATH = "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/hotel_search/hotel_search_output/hotels.json"

amadeus = Client(
    client_id = creds["API_KEY"],
    client_secret = creds["API_SECRET"]
)
print(Client.__doc__)

def load_json_file(conversation_history_path):
    with open(conversation_history_path, 'r') as file:
        result = json.load(file)
    return result

def get_iata_code_by_city(city_name):
    for code, info in airports.items():
        if city_name.lower() in info['city'].lower():
            return code
    return None


def search_hotels(destination):
    headers = {
        "Authorization": f"Bearer {creds["ACCESS_TOKEN"]}"
        }
    
    params = {
        "cityCode": get_iata_code_by_city(destination)
    }

    response = requests.get(creds["HOTEL_SEARCH_URL"], headers=headers, params=params)
    return response.json()

def confirm_hotels(hotel_search_results):
    print(hotel_search_results['data'][0]['hotelId'], entities['n_adults'], entities['departure_date'], entities['return_date'])
    result = amadeus.shopping.hotel_offers_search.get(
        hotelIds = "HNBLR968",
        adults = 1,
        checkInDate = "2025-09-08",
        checkOutDate = "2025-09-12"
    )
    return result

def save(result):
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    entities = load_json_file(PATH)
    print(get_iata_code_by_city(entities['destination']))
    hotel_search_results = search_hotels(entities['destination'])
    save(hotel_search_results)

