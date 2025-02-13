import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import random

# Initialize User-Agent rotation
ua = UserAgent()

# Use a session for persistent connections & automatic cookie handling
session = requests.Session()

# Target URL
base_url = "https://www.coches.net/segunda-mano/"

# Number of pages to scrape
num_pages = 5

# Loop through multiple pages
for page in range(1, num_pages + 1):
    url = f"{base_url}?pg={page}"
    
    # Rotate headers for each request
    headers = {
        "User-Agent": ua.random,
        "Accept-Encoding": str(random.randint(1, 10000000)),  # Random Accept-Encoding
        "Referer": "https://www.google.com/",  # Mimics a real user
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
    }
    
    print(f"📄 Scraping page {page}: {url}")
    
    # Send request
    response = session.get(url, headers=headers)
    
    # Check if blocked
    if "Ups! Parece que algo no va bien..." in response.text:
        print("🚨 Blocked! Retrying with new headers...\n")
        time.sleep(random.uniform(5, 10))
        continue
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract car links
    links = soup.find_all("a", class_="mt-CardAd-media")

    # Extract href attributes
    links_href = [link.get("href") for link in links if link.get("href")]

    # Process each car listing
    for link_href in links_href:
        car_url = f"https://www.coches.net{link_href}"
        print(f"🔗 Car URL: {car_url}")

        # Send request to car detail page
        car_response = session.get(car_url, headers=headers)
        time.sleep(random.uniform(5, 20))  # Delay to mimic human behavior

        car_soup = BeautifulSoup(car_response.text, "html.parser")

        # Extract car title
        title_elem = car_soup.find("h5", class_="mt-TitleBasic-title mt-TitleBasic-title--xs mt-TitleBasic-title--negro")
        title = title_elem.text.strip() if title_elem else "N/A"
        print(f"🚗 Car Title: {title}")

        # Extract car price
        price_elem = car_soup.find("h5", class_="mt-TitleBasic-title mt-TitleBasic-title--xs mt-TitleBasic-title--currentColor")
        price = price_elem.text.strip() if price_elem else "N/A"
        print(f"💰 Price: {price}")

        # Extract car features
        features = []
        ul_element = car_soup.find("ul", class_="mt-PanelAdDetails-data")
        if ul_element:
            features = [li.text.strip() for li in ul_element.find_all("li", class_="mt-PanelAdDetails-dataItem")]
            print(f"📌 Features: {', '.join(features)}")
        else:
            print("⚠ No features found.")

        print("\n" + "-" * 50 + "\n")

    # Random delay before the next page
    time.sleep(random.uniform(3, 7))

print("✅ Scraping complete.")
