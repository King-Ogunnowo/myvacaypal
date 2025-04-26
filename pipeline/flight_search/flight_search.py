from dotenv import load_dotenv
from airportsdata import load

import requests
import json
import os

load_dotenv()
airports = load("IATA")
PATH = "../entity_extraction/entity_extraction_output/entities.json"
OUTPUT_PATH = "flight_search_output/output.json"

def load_json_file(conversation_history_path):
    with open(conversation_history_path, 'r') as file:
        result = json.load(file)
    return result

def get_access_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": os.environ.get("API_KEY"),
        "client_secret": os.environ.get("API_SECRET")
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
        }
    response = requests.post(
        os.environ.get("TOKEN_URL"), 
        data=payload, 
        headers=headers
    )
    response_data = response.json()

    return response_data["access_token"], response_data["expires_in"]

def get_iata_code_by_city(city_name):
    for code, info in airports.items():
        if city_name.lower() in info['city'].lower():
            return code
    return None

def search_flights(trip_departure_date, trip_return_date, departure, destination, n_adults, n_children):
    access_token, expires_in = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}"
        }
    params = {
        "originLocationCode": get_iata_code_by_city(departure),
        "destinationLocationCode": get_iata_code_by_city(destination),
        "departureDate": trip_departure_date,
        "returnDate":trip_return_date,
        "adults":n_adults,
        "children":n_children,
        "currencyCode":"EUR"
    }
    response = requests.get(os.environ.get("FLIGHT_SEARCH_URL"), headers=headers, params=params)
    print(response.json())
    return response.json()

def save(result):
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    entities = load_json_file(PATH)
    print(os.environ.get("API_KEY"))
    result = search_flights(
        trip_departure_date = entities['departure_date'],
        trip_return_date = entities['return_date'],
        departure = entities['departure'],
        destination = entities['destination'],
        n_adults = entities['n_adults'],
        n_children = entities['n_children']
    )
    save(result)

