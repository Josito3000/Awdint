import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import random

# Initialize UserAgent for random headers
ua = UserAgent()

# Base URL of the website
base_url = "https://www.coches.net/segunda-mano/?pg="

# Function to scrape a single page
def scrape_page(page_number):
    url = f"{base_url}{page_number}"
    # Rotate headers for each request
    headers = {
        "User-Agent": ua.random,
        "Accept-Encoding": str(random.randint(1, 10000000)),  # Random Accept-Encoding
        "Referer": "https://www.google.com/",  # Mimics a real user
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
    }
    
    # Make request
    response = requests.get(url, headers=headers)
    
    # Check if the request was blocked
    if "Ups! Parece que algo no va bien..." in response.text:
        print(f"🚨 Blocked on page {page_number}, trying again...")
        time.sleep(random.uniform(5, 10))
        return scrape_page(page_number)  # Retry
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract car listings
    car_cards = soup.find_all("article", class_="mt-CardAd")
    
    # List to store extracted data
    cars_data = []

    for car in car_cards:
        # Extract title
        title_tag = car.find("span", class_="mt-CardAd-titleHiglight")
        title = title_tag.text.strip() if title_tag else "N/A"

        # Extract price
        price_tag = car.find("span", class_="mt-CardAd-price")
        price = price_tag.text.strip().replace(" €", "").replace(".", "") if price_tag else "N/A"

        # Extract link
        link_tag = car.find("a", class_="mt-CardAd-link")
        link = "https://www.coches.net" + link_tag["href"] if link_tag else "N/A"

        # Extract features (location, model, year, km, etc.)
        features = car.find_all("li", class_="mt-CardAd-attribute")
        location = features[0].text.strip() if len(features) > 0 else "N/A"
        engine = features[1].text.strip() if len(features) > 1 else "N/A"
        year = features[2].text.strip() if len(features) > 2 else "N/A"
        km = features[3].text.strip().replace(" km", "").replace(".", "") if len(features) > 3 else "N/A"

        # Print the extracted details
        print(f"✅ {title} - {price}€ - {location}, {year}, {km}km")
        
        # Store in a list
        cars_data.append({
            "title": title,
            "price": price,
            "location": location,
            "engine": engine,
            "year": year,
            "km": km,
            "link": link
        })

    return cars_data

# Run the scraper for the first 3 pages (change range as needed)
all_cars = []
for page in range(1, 4):
    print(f"\n🔄 Scraping Page {page}...")
    cars = scrape_page(page)
    all_cars.extend(cars)
    time.sleep(random.uniform(3, 7))  # Randomized delay

# Save to CSV
import pandas as pd
df = pd.DataFrame(all_cars)
df.to_csv("coches_data.csv", index=False, encoding="utf-8-sig")
print("\n✅ Data saved to coches_data.csv")
