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

for i in range(1):
    URL = 'https://www.coches.net/segunda-mano/'
    r = session.get(URL, headers=headers)
    print(r.content)

    time.sleep(random.uniform(3 + i, 7 + i))

    soup = BeautifulSoup(r.content, 'html.parser')
    print(soup)

    # Extract car links
    links = soup.find_all('a', class_="mt-CardAd-media")

    # Extract the href attribute for each link in the result set
    links_href = [link.get('href') for link in links]

    # Print the link of each car
    for link_href in links_href:
        print("ENLACE: ", link_href)
        new_link = "https://www.coches.net/segunda-mano" + link_href
        r = session.get(new_link, headers=headers)

        time.sleep(random.uniform(15 + i, 20 + i))

        soup = BeautifulSoup(r.content, 'html.parser')
        # Extract car titles
        car_titles = soup.find_all("h5",
                                   class_="mt-TitleBasic-title mt-TitleBasic-title--xs mt-TitleBasic-title--negro")
        for title in car_titles:
            print("NOM: ", title.text)

        # Extract car prices
        prices = soup.find_all("h5",
                               class_="mt-TitleBasic-title mt-TitleBasic-title--xs mt-TitleBasic-title--currentColor")
        for price in prices:
            print("PREU: ", price.text)

        # Extract features
        ul_element = soup.find("ul", class_="mt-PanelAdDetails-data")
        if ul_element:
            for li_element in ul_element.find_all("li", class_="mt-PanelAdDetails-dataItem"):
                print("Características: ", li_element.text)
        else:
            print("No se encontró ningún elemento <ul> con la clase 'mt-PanelAdDetails-data'.")
            time.sleep(random.uniform(1800, 1805))
