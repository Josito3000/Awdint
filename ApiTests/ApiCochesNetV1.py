import requests
import json
import time
import random
import pandas as pd
from fake_useragent import UserAgent

# Initialize User-Agent rotation
ua = UserAgent()

# API URL
api_url = "https://web.gw.coches.net/search"

# Headers (Important to avoid being blocked)
headers = {
        "User-Agent": ua.random,
        "Accept-Encoding": str(random.randint(1, 10000000)),  # Random Accept-Encoding
        "Referer": "https://www.google.com/",  # Mimics a real user
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
    }

# Number of pages to scrape
num_pages = 3  # Change this to get more pages
cars_list = []

for page in range(1, num_pages + 1):
    print(f"📄 Scraping page {page}...")

    # JSON payload for POST request
    payload = {
        "pagination": {
            "page": page,
            "size": 30  # Number of cars per page
        },
        "sort": {
            "order": "desc",
            "term": "relevance"
        },
        "filters": {
            "offerTypeIds": [10]  # Second-hand cars
        }
    }

    # Make POST request
    response = requests.post(api_url, headers=headers, json=payload)
    print(response.text)

    # Check if blocked
    if response.status_code != 200:
        print(f"🚨 Blocked or error {response.status_code}. Retrying...")
        time.sleep(random.uniform(5, 10))
        continue

    try:
        data = response.json()
        listings = data.get("listings", [])

        for car in listings:
            car_data = {
                "Title": car.get("title", "N/A"),
                "Price (€)": car.get("price", "N/A"),
                "Make": car.get("make", {}).get("name", "N/A"),
                "Model": car.get("model", {}).get("name", "N/A"),
                "Year": car.get("firstRegistrationYear", "N/A"),
                "Mileage (km)": car.get("kilometers", "N/A"),
                "Fuel": car.get("fuelType", {}).get("name", "N/A"),
                "Location": car.get("location", {}).get("province", {}).get("name", "N/A"),
                "URL": f"https://www.coches.net{car.get('url', '')}"
            }
            cars_list.append(car_data)

    except json.JSONDecodeError:
        print("❌ Failed to parse JSON")
    
    # Random delay before the next page request
    time.sleep(random.uniform(3, 7))

# Convert to Pandas DataFrame and save to Parquet
df = pd.DataFrame(cars_list)
df.to_parquet("coches_net_listings.parquet", index=False)
print("✅ Scraping complete. Data saved to 'coches_net_listings.parquet'.")

