import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from fake_useragent import UserAgent
import random
from datetime import datetime

# Initialize User-Agent rotation
ua = UserAgent()

# Use a session for persistent connections & automatic cookie handling
session = requests.Session()

# Read URLs from file
file_path = "car_links_2025-02-19_15-08.txt"  # Change if needed
with open(file_path, "r", encoding="utf-8") as file:
    car_urls = [line.strip() for line in file.readlines()]

#car_urls = car_urls[:100]

# List to store scraped data
car_data = []

start = (time.time())

# Loop through each car URL
for index, car_url in enumerate(car_urls, start=1):
    # Rotate headers for each request
    headers = {
        "User-Agent": ua.random,
        "Accept-Encoding": str(random.randint(1, 10000000)),  # Random Accept-Encoding
        "Referer": "https://www.google.com/",  # Mimics a real user
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
    }

    print(f"🔗 Scraping car {index}/{len(car_urls)}: {car_url}")

    try:
        # Send request to car detail page
        car_response = session.get(car_url, headers=headers, timeout=15)
        
        # Check if blocked
        if "Ups! Parece que algo no va bien..." in car_response.text:
            print("🚨 Blocked! Retrying with new headers...\n")
            #time.sleep(random.uniform(5, 10))
            continue

        car_soup = BeautifulSoup(car_response.text, "html.parser")

        # Extract car title
        title_elem = car_soup.find("h1")
        title = title_elem.text.strip() if title_elem else "N/A"
        print(f"🚗 Title: {title}")

        # Extract car price
        price_elem = car_soup.find("h3", class_="mt-TitleBasic-title mt-TitleBasic-title--s mt-TitleBasic-title--currentColor")
        price = price_elem.text.strip() if price_elem else "N/A"
        print(f"💰 Price: {price}")

        # Extract car features
        features = []
        ul_element = car_soup.find("ul", class_="mt-PanelAdDetails-data")
        if ul_element:
            features = [li.text.strip() for li in ul_element.find_all("li", class_="mt-PanelAdDetails-dataItem")]
        print(f"📌 Features: {', '.join(features) if features else '⚠ No features found'}")

        # Append data to the list
        car_data.append({
            "Title": title,
            "Price": price,
            "Features": ", ".join(features),
            "URL": car_url
        })

    except Exception as e:
        print(f"⚠ Error scraping {car_url}: {e}")

    # Random delay before the next request
    #time.sleep(random.uniform(5, 12))

print(time.time()-start)
print("✅ Scraping complete.")

# Convert data to a DataFrame
df = pd.DataFrame(car_data)

# Save as Parquet
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

#parquet_filename = "coches_data_{timestamp}.parquet"
#df.to_parquet(parquet_filename, engine="pyarrow", index=False)
#print(f"✅ Data saved to '{parquet_filename}'")
