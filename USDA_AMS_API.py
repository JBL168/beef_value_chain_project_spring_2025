import requests, pandas as pd, os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

API_KEY = os.getenv("USDA_API_KEY")
BASE_URL = "https://marsapi.ams.usda.gov/services/v1.2/reports/"
SLUG_ID = "3232" # Slug ID for National Feeder & Stocker Cattle Summary


r = requests.get(f"{BASE_URL}{SLUG_ID}", auth=HTTPBasicAuth(API_KEY, ''))

if r.status_code == 200:
    data = r.json()
    print("Data retrieved successfully:")
    print(data)
else:
    print(f"Error: {r.status_code}, {r.text}")