from amadeus import Client, ResponseError
from dotenv import load_dotenv

import json
import os

load_dotenv()

flight_offer_path = "flight_search_output/flight_search_output.json"
amadeus = Client(
    client_id=os.environ.get('API_KEY'),
    client_secret=os.environ.get('API_SECRET'),

)
flight_price_confirmation_output_path = "flight_search_output/flight_price_confirmation_price.json"

def load_file(flight_offer_path):
    with open(flight_offer_path, 'r') as file:
        result = json.load(file)
    return result


def confirm_flights(search_flights_results):
    result = amadeus.shopping.flight_offers.pricing.post(
        search_flights_results['data'][0]
    )
    print(result.data)
    return result.data

def save(result):
    with open(flight_price_confirmation_output_path, "w") as f:
        json.dump(result, f, indent=4)


if __name__ == "__main__":
    flight_offers = load_file(flight_offer_path)
    confirmed_flight_offers = confirm_flights(flight_offers)
    save(confirmed_flight_offers)


