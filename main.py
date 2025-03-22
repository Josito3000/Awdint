#Python built-in libraries
import time
import random
import os 
#First party libraries
from utils.helpers import *

#Third party libreries
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Initialize User-Agent rotation
ua = UserAgent()

# Use a session for persistent connections & automatic cookie handling
session = requests.Session()

# Target URL
base_url = os.getenv("URL")

# Number of pages to scrape
num_pages = 2

# Loop through multiple pages
for page in range(1, num_pages + 1):
    url = f"{base_url}?pg={page}"
    
    # Rotate headers for each request
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1"
    }
    
    print(f"📄 Scraping page {page}: {url}")

    try:
        # Send request with increased timeout
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Check if blocked
        if "Ups! Parece que algo no va bien..." in response.text:
            print("🚨 Blocked! Retrying with new headers...\n")
            time.sleep(random.uniform(10, 15))
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Actualizamos los selectores para encontrar los enlaces de coches
        links = soup.select("a[data-testid='mt-ad-card']") or \
                soup.select("article.mt-CardAd a.mt-CardAd-media") or \
                soup.find_all("a", class_="mt-CardAd-media")

        if not links:
            print(f"⚠️ No se encontraron enlaces en la página {page}")
            continue

        print(f"🔍 Encontrados {len(links)} enlaces en la página {page}")

        # Extract href attributes
        links_href = [link.get("href") for link in links if link.get("href")]

        # Process each car listing
        for link_href in links_href:
            car_url = f"https://www.coches.net{link_href}"
            print(f"🔗 Car URL: {car_url}")

            # Send request to car detail page
            car_response = session.get(car_url, headers=headers)
            time.sleep(random.uniform(15, 20))  # Delay to mimic human behavior

            car_soup = BeautifulSoup(car_response.text, "html.parser")

            # Extract car title
            title_elem = car_soup.find("h1", class_= "mt-TitleBasic-title mt-TitleBasic-title--s mt-TitleBasic-title--black")
            title = transformation(title_elem)
            #with open('data.html', 'w', encoding='utf-8') as file:
            #    file.write(car_soup.prettify())
            print(f"🚗 Car Title: {title}")

            # Extract car price
            price_elem = car_soup.find("h3", class_="mt-TitleBasic-title mt-TitleBasic-title--s mt-TitleBasic-title--currentColor")
            price = transformation(price_elem)
            print(f"💰 Price: {price}")

            # Extract car features
            features = []
            ul_element = car_soup.find("ul", class_="mt-PanelAdDetails-data")
            if ul_element:
                features = [li.text.strip() for li in ul_element.find_all("li", class_="mt-PanelAdDetails-dataItem")]
                print(f"📌 Features: {', '.join(features)}")
            else:
                print("⚠ No features found.")

            desc_elem = car_soup.find("div", class_="mt-PanelAdDetails-commentsContent" , attrs = {"data-testid": "mt-PanelAdDetails-description"})
            desc = transformation(desc_elem)
            print(f"📝 Descripción: {desc}")

            rate_elem = car_soup.find("p", class_="mt-RatingBasic-infoValue")
            rate = transformation(rate_elem)
            print(f"🌟 Rating: {rate}")

            print("\n" + "-" * 50 + "\n")

        # Random delay before the next page
        time.sleep(random.uniform(3, 7))

    except requests.exceptions.RequestException as e:
        print(f"🚫 Error al acceder a la página {page}: {e}")
        continue

print("✅ Scraping complete.")
