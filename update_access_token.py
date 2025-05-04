from dotenv import load_dotenv, dotenv_values

import subprocess
import requests
import os


credentials = dict(dotenv_values(".env"))
load_dotenv()


def update_access_key(credentials, new_access_key, env_file):
    credentials['ACCESS_TOKEN'] = new_access_key
    with open(env_file, "w") as f:
        for key, value in credentials.items():
            f.write(f'{key}="{value}"\n')

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


if __name__ == "__main__":
    access_token, expires_in = get_access_token()
    print(access_token)
    update_access_key(
        credentials = credentials,
        new_access_key = get_access_token()[0],
        env_file = ".env"
    )


