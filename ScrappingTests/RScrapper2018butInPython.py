import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from fake_useragent import UserAgent

# Function to scrape car listings from coches.net
def scrape_coches(output_file="coches.csv", pages=1):
    start_time = time.time()
    
    # List of user agents to rotate
    ua = UserAgent()
    
    # Create CSV file with headers
    columns = ["Titulo", "Marca", "Precio", "Provincia", "Motor", "Año", "Kilometros", "Fecha subida", "Link"]
    df = pd.DataFrame(columns=columns)
    df.to_csv(output_file, mode='w', index=False, encoding="utf-8-sig")
    
    for page in range(1, pages + 1):
        url = f"https://www.coches.net/segunda-mano/?pg={page}"
        print(f"📄 Scraping: {url}")

        headers = {"User-Agent": ua.random}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to retrieve page {page}. Status code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        car_blocks = soup.find_all("div", class_="mt-Card-body")

        for car in car_blocks:
            # Extract title
            title_elem = car.select_one(".mt-CardAd-title .mt-CardAd-titleHiglight")
            titulo = title_elem.text.strip() if title_elem else "N/A"

            # Extract brand
            marca = titulo.split(" ")[0] if titulo != "N/A" else "N/A"

            # Extract price
            price_elem = car.select_one(".mt-CardAd-price .mt-CardAd-titleHiglight")
            precio = price_elem.text.strip().replace(" €", "").replace(".", "") if price_elem else "N/A"
            precio = int(precio) if precio.isnumeric() else "N/A"

            # Extract additional info (province, engine, year, km)
            info_elems = car.select(".mt-CardAd-attribute")
            provincia, motor, anio, km = ["N/A"] * 4
            if len(info_elems) >= 4:
                provincia = info_elems[0].text.strip()
                motor = info_elems[1].text.strip()
                anio = info_elems[2].text.strip()
                km = info_elems[3].text.strip().replace(" km", "").replace(".", "")
                km = int(km) if km.isnumeric() else "N/A"

            # Extract posting date
            date_elem = car.select_one(".mt-CardAdDate-time")
            fecha_subida = date_elem.text.strip() if date_elem else "N/A"

            # Extract link
            link_elem = car.select_one(".mt-CardAd-link")
            link = "https://www.coches.net" + link_elem["href"] if link_elem else "N/A"

            # Print and save results
            print(f"🚗 {titulo} | {marca} | 💰 {precio}€ | 📍 {provincia} | ⚙ {motor} | 📅 {anio} | 🚗 {km}km | 🕒 {fecha_subida} | 🔗 {link}")
            df = pd.DataFrame([[titulo, marca, precio, provincia, motor, anio, km, fecha_subida, link]], columns=columns)
            df.to_csv(output_file, mode='a', header=False, index=False, encoding="utf-8-sig")

        # Random delay to mimic human behavior
        time.sleep(random.uniform(3, 6))

    end_time = time.time()
    print(f"✅ Scraping complete in {round(end_time - start_time, 2)} seconds.")

# Run the scraper for 5 pages
scrape_coches(output_file="coches_scraped.csv", pages=5)
