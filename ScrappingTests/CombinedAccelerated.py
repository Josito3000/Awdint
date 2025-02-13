import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import random
import pandas as pd

# Initialize User-Agent rotation
ua = UserAgent()

# Base URL of the website
base_url = "https://www.coches.net/segunda-mano/"

# Number of pages to scrape
num_pages = 5

# List to store scraped data
cars_data = []

# Function to scrape a single page
def scrape_page(page_number):
    url = f"{base_url}?pg={page_number}"
    
    # Rotate headers for each request
    headers = {
        "User-Agent": ua.random,
        "Accept-Encoding": str(random.randint(1, 10000000)),  # Random Accept-Encoding
        "Referer": "https://www.google.com/",  # Mimics a real user
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
    }
    
    print(f"📄 Scraping page {page_number}: {url}")
    
    # Start a new session every 3 pages
    if page_number % 3 == 0:
        session = requests.Session()
    else:
        session = requests
    
    # Send request
    response = session.get(url, headers=headers)
    
    # Check if blocked
    if "Ups! Parece que algo no va bien..." in response.text:
        print("🚨 Blocked! Retrying with new headers...\n")
        time.sleep(random.uniform(5, 10))
        return scrape_page(page_number)  # Retry
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract car listings directly from the list page
    car_cards = soup.find_all("article", class_="mt-CardAd")

    for car in car_cards:
        try:
            # Extract title
            title_tag = car.find("span", class_="mt-CardAd-titleHiglight")
            title = title_tag.text.strip() if title_tag else "N/A"

            # Extract price directly from the list page
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
            print(f"✅ {title} - {price}€ - {location}, {year}, {km}km - 🔗 {link}")
            
            # Store in list
            cars_data.append({
                "title": title,
                "price": price,
                "location": location,
                "engine": engine,
                "year": year,
                "km": km,
                "link": link
            })

        except Exception as e:
            print(f"❌ Error extracting a car: {e}")
    
    # Lower the sleep time to balance speed vs. avoiding bans
    time.sleep(random.uniform(2, 5))

# Run the scraper for multiple pages
for page in range(1, num_pages + 1):
    scrape_page(page)

# Save to CSV
df = pd.DataFrame(cars_data)
df.to_csv("coches_data_fast.csv", index=False, encoding="utf-8-sig")
print("\n✅ Data saved to coches_data_fast.csv")
