import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# Launch undetected Chrome
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
options.add_argument("start-maximized")  # Open full screen like a real user
options.add_argument("--disable-extensions")  # Mimic a clean browser
options.add_argument("--incognito")  # Use incognito mode to prevent tracking

# Start the browser
driver = uc.Chrome(options=options)

# Target URL
base_url = "https://www.coches.net/segunda-mano/"
num_pages = 100

# Open (or create if it doesn't exist) a file in append mode:
with open("car_links_100pages.txt", "a", encoding="utf-8") as outfile:

    for page in range(1, num_pages + 1):
        url = f"{base_url}?pg={page}"
        print(f"📄 Loading page {page}: {url}")

        driver.get(url)
        time.sleep(random.uniform(1, 2))  # Human-like wait time

        # Simulate human scrolling and waiting for JavaScript to load
        for _ in range(random.randint(35, 40)):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(0.1, 1))  # Vary the delay for realism

        # Get fully loaded HTML
        html_content = driver.page_source

        # (Optional) Save the HTML for debugging
        #with open(f"coches_net_rendered_{page}.html", "w", encoding="utf-8") as file:
        #    file.write(html_content)

        print(f"✅ Page {page} saved to coches_net_rendered_{page}.html")

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

driver.quit()  # Close browser session
print("✅ Scraping complete. Links saved to car_links.txt.")
