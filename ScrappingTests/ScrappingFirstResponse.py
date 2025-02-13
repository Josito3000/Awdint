import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import random

# Initialize the UserAgent object
ua = UserAgent()

headers = {
    'User-Agent': ua.random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
}

# Use a session for persistent connections and automatic cookie handling
session = requests.Session()

URL = 'https://www.coches.net/segunda-mano/'

# Send a request and save the HTML response
response = session.get(URL, headers=headers)

# Save the content to an HTML file
with open("coches_net_page.html", "w", encoding="utf-8") as file:
    file.write(response.text)

print("✅ HTML content saved as 'coches_net_page.html'")
