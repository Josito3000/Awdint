import os
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from fake_useragent import UserAgent
import random
from datetime import datetime

def scrape_folder(folder_path, output_filename=None, limit_per_file=None, output_folder="C:/Users/PORTATIL/OneDrive/Documentos/Projects/CochecitosScrapping/OutputData"):
    """
    Scrapes car details from all link files in a given folder and saves the data as a Parquet file.
    
    Args:
    - folder_path (str): Path to the folder containing .txt files with car links.
    - output_filename (str, optional): Name of the output .parquet file. Defaults to "coches_data_TIMESTAMP.parquet".
    - limit_per_file (int, optional): Limit of links to scrape per file. Default is None (scrape all links).
    
    Returns:
    - DataFrame containing scraped car details.
    """
    
    # Initialize User-Agent rotation
    ua = UserAgent()

    # Use a session for persistent connections & automatic cookie handling
    session = requests.Session()

    # List to store scraped data
    car_data = []

    start_time = time.time()

    # Get all text files in the folder
    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    
    print(f"📂 Found {len(files)} files in '{folder_path}'. Starting scraping...")

    # Loop through each file
    for file in files:
        file_path = os.path.join(folder_path, file)
        
        # Read URLs from file
        with open(file_path, "r", encoding="utf-8") as f:
            car_urls = [line.strip() for line in f.readlines()]
        
        # Limit the number of links if specified
        if limit_per_file:
            car_urls = car_urls[:limit_per_file]
        
        print(f"📄 Processing {file} ({len(car_urls)} links)")

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

            print(f"🔗 Scraping car {index}/{len(car_urls)} from {file}: {car_url}")

            try:
                # Send request to car detail page
                car_response = session.get(car_url, headers=headers, timeout=15)
                
                # Check if blocked
                if "Ups! Parece que algo no va bien..." in car_response.text:
                    print("🚨 Blocked! Retrying with new headers...\n")
                    continue

                car_soup = BeautifulSoup(car_response.text, "html.parser")

                # Extract car title
                title_elem = car_soup.find("h1")
                title = title_elem.text.strip() if title_elem else "N/A"

                # Extract car price
                price_elem = car_soup.find("h3", class_="mt-TitleBasic-title mt-TitleBasic-title--s mt-TitleBasic-title--currentColor")
                price = price_elem.text.strip() if price_elem else "N/A"
                print(f"💰 Price: {price}")

                # Extract car features
                features = []
                ul_element = car_soup.find("ul", class_="mt-PanelAdDetails-data")
                if ul_element:
                    features = [li.text.strip() for li in ul_element.find_all("li", class_="mt-PanelAdDetails-dataItem")]

                # Append data to the list
                car_data.append({
                    "Title": title,
                    "Price": price,
                    "Features": ", ".join(features),
                    "URL": car_url,
                    "Source File": file  # To track which file the link came from
                })

            except Exception as e:
                print(f"⚠ Error scraping {car_url}: {e}")

            # Random delay before the next request to avoid detection
            # time.sleep(random.uniform(5, 12))

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Convert data to a DataFrame
    df = pd.DataFrame(car_data)

    # Generate the filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_filename = os.path.join(output_folder, f"coches_data_consolidado_{timestamp}.parquet")

    # Save DataFrame to Parquet
    df.to_parquet(output_filename, engine="pyarrow", index=False)

    print(f"✅ Data saved to: {output_filename}")

    print("✅ Scraping complete")
    print(f"⏳ Total execution time: {time.time() - start_time:.2f} seconds")

    return df  # Return DataFrame for further processing if needed

scrape_folder("C:\\Users\\PORTATIL\\OneDrive\\Documentos\\Projects\\CochecitosScrapping\\CarLinks")
