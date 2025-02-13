import requests
from fake_useragent import UserAgent
import random
import time

# Initialize User-Agent rotation
ua = UserAgent()

# Target URL
url = "https://www.coches.net/segunda-mano/?pg=1"

# Generate headers
headers = {
    "User-Agent": ua.random,
    "Accept-Encoding": str(random.randint(1, 10000000)),  # Random Accept-Encoding
    "Referer": "https://www.google.com/",  # Mimic real users
    "Accept-Language": "en-US,en;q=0.9",
    "DNT": "1",
}

# Send request
response = requests.get(url, headers=headers)

# Save the HTML content
with open("coches_net_page_1.html", "w", encoding="utf-8") as file:
    file.write(response.text)

print("✅ Page source saved as 'coches_net_page_1.html'. Upload this file here.")
