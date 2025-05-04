from amadeus import Client, ResponseError
from dotenv import dotenv_values
from airportsdata import load

import pandas as pd
import subprocess
import requests
import amadeus
import json
import os

credentials = dict(dotenv_values("/Users/oluwaseyi/Documents/repositories/myvacaypal/.env"))

airports = load("IATA")
PATH = "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/entity_extraction/entity_extraction_output/entities.json"
OUTPUT_PATH = "/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/flight_search/flight_search_output/flight.json"
amadeus = Client(
    client_id=credentials['API_KEY'],
    client_secret=credentials['API_SECRET']
)

def load_json_file(conversation_history_path):
    with open(conversation_history_path, 'r') as file:
        result = json.load(file)
    return result

def get_iata_code_by_city(city_name):
    for code, info in airports.items():
        if city_name.lower() in info['city'].lower():
            return code
    return None

def search_flights(trip_departure_date, trip_return_date, departure, destination, n_adults, n_children):
    headers = {
        "Authorization": f"Bearer {credentials["ACCESS_TOKEN"]}"
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
    response = requests.get(credentials["FLIGHT_SEARCH_URL"], headers=headers, params=params)
    return response.json()

def confirm_flights(search_flights_results):
    result = amadeus.shopping.flight_offers.pricing.post(
        search_flights_results['data'][0:3]
    )
    print(result.data)
    return result.data

def get_top_n_flights_by_price(flights, n):
    sorted_offers = sorted(flights, key=lambda x: float(x["price"]["grandTotal"]))
    return sorted_offers[:n]

def flatten_flight_segments_with_price(data):
    """
    Flattens flight segment data and includes total price from Amadeus flight offers.

    Args:
        data (dict): The JSON data structure containing flight offers.

    Returns:
        pd.DataFrame: Flattened DataFrame with segments and total price.
    """
    flattened_segments = []

    for offer in data.get("flightOffers", []):
        offer_id = offer.get("id")
        total_price = offer.get("price", {}).get("total")

        for itinerary_index, itinerary in enumerate(offer.get("itineraries", [])):
            for seg_index, seg in enumerate(itinerary.get("segments", [])):
                flat_seg = {
                    "offer_id": offer_id,
                    "total_price": total_price,
                    "itinerary_index": itinerary_index,
                    "segment_index": seg_index
                }

                def flatten_dict(d, parent_key=""):
                    items = []
                    for k, v in d.items():
                        new_key = f"{parent_key}_{k}" if parent_key else k
                        if isinstance(v, dict):
                            items.extend(flatten_dict(v, new_key).items())
                        elif isinstance(v, list) and all(isinstance(i, dict) for i in v):
                            for idx, item in enumerate(v):
                                items.extend(flatten_dict(item, f"{new_key}_{idx}").items())
                        else:
                            items.append((new_key, v))
                    return dict(items)

                flat_seg.update(flatten_dict(seg))
                flattened_segments.append(flat_seg)

    return pd.DataFrame(flattened_segments)

def save(result):
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    entities = load_json_file(PATH)
    flights_search_result = search_flights(
        trip_departure_date = entities['departure_date'],
        trip_return_date = entities['return_date'],
        departure = entities['departure'],
        destination = entities['destination'],
        n_adults = entities['n_adults'],
        n_children = entities['n_children']
    )
    flights_confirmed_result = confirm_flights(flights_search_result)
    save(flights_confirmed_result)
    flattened = flatten_flight_segments_with_price(flights_confirmed_result)
    flattened.to_csv("/Users/oluwaseyi/Documents/repositories/myvacaypal/pipeline/flight_search/flight_search_output/flattened_flight_confirmation_results.csv", index = False)

    
    

