import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime

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
num_pages = 8500

# Load first page
driver.get(base_url)
time.sleep(5)  # Wait for cookies pop-up to appear

restart_every = 25

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
# Open (or create if it doesn't exist) a file in append mode:
with open(f"car_links_{timestamp}.txt", "a", encoding="utf-8") as outfile:

    for page in range(8000, num_pages + 1):

        url = f"{base_url}?pg={page}"
        print(f"📄 Loading page {page}: {url}")

        driver.get(url)
        time.sleep(random.uniform(0.25, 1))  # Human-like wait time

        driver.execute_script("document.body.style.zoom='3%'")

        # Simulate human scrolling and waiting for JavaScript to load
        for _ in range(random.randint(4, 6)):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(0.1, 0.15))  # Vary the delay for realism

        # Get fully loaded HTML
        html_content = driver.page_source

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

