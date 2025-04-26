from dotenv import load_dotenv

import subprocess
import requests
import os


load_dotenv()

def update_env_var(key, value, env_file=".env"):
    try:
        with open(env_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    key_found = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key} = "):
            new_lines.append(f"{key} = {value}\n")
            key_found = True
        else:
            new_lines.append(line)

    if not key_found:
        new_lines.append(f"\n{key}={value}\n")

    with open(env_file, "w") as f:
        f.writelines(new_lines)

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
    update_env_var(
        key = "ACCESS_TOKEN",
        value = access_token
    )
    subprocess.run(["python", "flight_search.py"])
    subprocess.run(["python", "flight_price_confirmation.py"])


