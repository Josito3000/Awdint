import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime
import os

import requests
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from fake_useragent import UserAgent


def greet():
    print("greetings")
    
def ScrapeMainPageListings_Selenium_ListFileOutput(
    base_url = "https://www.coches.net/segunda-mano/",
    start_page = 1,
    output_folder="C:/Users/PORTATIL/OneDrive/Documentos/Projects/CochecitosScrapping/CarLinks2",


        
):
    # Launch undetected Chrome
    options = uc.ChromeOptions()
    #options.add_argument("--headless=new")  # Runs Chrome in headless mode but doesn't load the content so avoid
    options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
    options.add_argument("start-maximized")  # Open full screen like a real user
    options.add_argument("--disable-extensions")  # Mimic a clean browser
    options.add_argument("--incognito")  # Use incognito mode to prevent tracking

    # Start the browser
    driver = uc.Chrome(options=options)

    # Load first page
    driver.get(base_url)
    time.sleep(15)  # Wait for cookies pop-up to appear


    num_pages = 8500

    restart_every = 25

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    os.makedirs(output_folder, exist_ok=True)
    file_path = os.path.join(output_folder, f"car_links_{timestamp}.txt")
    
    with open(file_path, "a", encoding="utf-8") as outfile:

        for page in range(start_page, num_pages + 1):

            url = f"{base_url}?pg={page}"
            print(f"📄 Loading page {page}: {url}")

            driver.get(url)
            time.sleep(random.uniform(0.5, 1))  # Human-like wait time

            driver.execute_script("document.body.style.zoom='2%'")

            # Simulate human scrolling and waiting for JavaScript to load
            #for _ in range(random.randint(4, 7)):
            #    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            #    time.sleep(random.uniform(0.05, 0.10))  # Vary the delay for realism

            time.sleep(0.1)

            # Get fully loaded HTML
            html_content = driver.page_source

             # Check if blocked
            if "Ups! Parece que algo no va bien..." in html_content:
                print(f"🚨 Blocked on page {page}")
                #time.sleep(random.uniform(5, 10))  # Wait before retrying
                driver.quit()  # Close browser session
                print("Waiting for the next opening")
                return None  # Skip to the next page

            # (Optional) Save the HTML for debugging
            #with open(f"coches_net_rendered_{page}.html", "w", encoding="utf-8") as file:
            #    file.write(html_content)

            #print(f"✅ Page {page} saved to coches_net_rendered_{page}.html")


            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
        
            # Extract car links
            links = soup.find_all("a", class_="mt-CardAd-media")
            links_href = [f"https://www.coches.net{link.get('href')}"
                        for link in links if link.get("href")]

            print(f"🔗 Extracted {len(links_href)} car links")

            # Write each link to the file
            for link in links_href:
                outfile.write(link + "\n")

            if page % restart_every == 0:
                time.sleep(random.uniform(2, 3))

    driver.quit()  # Close browser session
    print("✅ Scraping complete. Links saved to car_links.txt.")

    return timestamp

# Initialize User-Agent rotation
ua = UserAgent()

# Use a session for persistent connections & automatic cookie handling
session = requests.Session()


def ScrapeCarListing(
    car_url,
    source_file=None
):
    
    headers = {
                "User-Agent": ua.random,
                "Accept-Encoding": str(random.randint(1, 10000000)),  # Random Accept-Encoding
                "Referer": "https://www.google.com/",  # Mimics a real user
                "Accept-Language": "en-US,en;q=0.9",
                "DNT": "1",
            }

    try:
        # Send request to car detail page
        car_response = session.get(car_url, headers=headers, timeout=15)
        
        # Check if blocked
        if "Ups! Parece que algo no va bien..." in car_response.text:
            print(f"🚨 Blocked on: {car_url}")
            return None  # Skip this entry

        soup = BeautifulSoup(car_response.text, "html.parser")

        # Extract car details
        title = soup.find("h1").text.strip() if soup.find("h1") else "N/A"
        price = soup.find("h3", class_="mt-TitleBasic-title mt-TitleBasic-title--s mt-TitleBasic-title--currentColor")
        price = price.text.strip() if price else "N/A"
        print(f"💰 Price: {price}")
        # Extract features
        features = []
        ul_element = soup.find("ul", class_="mt-PanelAdDetails-data")
        if ul_element:
            features = [li.text.strip() for li in ul_element.find_all("li", class_="mt-PanelAdDetails-dataItem")]

        return {
            "Title": title,
            "Price": price,
            "Features": ", ".join(features),
            "URL": car_url,
            "Scrape Date": datetime.now().strftime("%Y-%m-%d"),
            "Source File": source_file  # Store source file for tracking
        }

    except Exception as e:
        print(f"⚠ Error scraping {car_url}: {e}")
        return None

def scrape_folder_links(folder_path, output_folder="C:/Users/PORTATIL/OneDrive/Documentos/Projects/CochecitosScrapping/OutputData", limit_per_file=None):
    """
    Scrapes car details from all link files in a folder and saves the data as a Parquet file.

    Args:
    - folder_path (str): Path to the folder containing .txt files with car links.
    - output_folder (str): Path to save the output Parquet file.
    - limit_per_file (int, optional): Limit of links to scrape per file.

    Returns:
    - DataFrame: A DataFrame containing all scraped car details.
    """
    start_time = time.time()

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get all text files in the folder
    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    print(f"📂 Found {len(files)} files in '{folder_path}'. Starting scraping...")

    # List to store scraped data
    car_data = []

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

        # Scrape each car URL
        for index, car_url in enumerate(car_urls, start=1):
            print(f"🔗 Scraping car {index}/{len(car_urls)} from {file}: {car_url}")

            car_details = ScrapeCarListing(car_url, source_file=file)
            if car_details:
                car_data.append(car_details)

            # Random delay before the next request to avoid detection
            #time.sleep(random.uniform(5, 12))

    # Convert data to a DataFrame
    df = pd.DataFrame(car_data)

    # Generate the filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_filename = os.path.join(output_folder, f"coches_data_compiled_{timestamp}.parquet")

    # Save DataFrame to Parquet
    df.to_parquet(output_filename, engine="pyarrow", index=False)

    print(f"✅ Data saved to: {output_filename}")
    print(f"✅ Scraping complete in {time.time() - start_time:.2f} seconds.")

    return df 