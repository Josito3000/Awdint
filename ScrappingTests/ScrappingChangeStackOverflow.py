import requests
from bs4 import BeautifulSoup
import random
import time
from fake_useragent import UserAgent

# Generate random User-Agent
ua = UserAgent()

# Define the target URL
url = "https://www.coches.net/segunda-mano/"

# Number of tries
for i in range(10):
    headers = {
        "User-Agent": ua.random,  # Random User-Agent
        "Accept-Encoding": str(random.randint(1, 10000000)),  # Random Accept-Encoding
        "Referer": "https://www.google.com/",  # Fake referer to mimic a real user
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",  # Do Not Track header
    }

    print(f"🔄 Try {i+1} with headers: {headers}")
    
    # Send request
    response = requests.get(url, headers=headers)
    
    # Check if blocked
    if "Ups! Parece que algo no va bien..." in response.text:
        print("🚨 Blocked! Trying again with new headers...\n")
        time.sleep(random.uniform(5, 10))  # Random delay
        continue
    
    # Parse response
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract the title
    title = soup.find("title")
    print(f"✅ Page Title: {title.text.strip() if title else 'N/A'}\n")

    # Random wait time before the next request
    time.sleep(random.uniform(3, 7))
