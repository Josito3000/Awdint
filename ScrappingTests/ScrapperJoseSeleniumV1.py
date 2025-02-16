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
num_pages = 3

for page in range(1, num_pages + 1):
    url = f"{base_url}?pg={page}"
    print(f"📄 Loading page {page}: {url}")

    driver.get(url)
    time.sleep(random.uniform(3, 6))  # Human-like wait time

    # Simulate human scrolling and waiting for JavaScript to load
    for _ in range(random.randint(6, 10)):  
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(random.uniform(1, 3))  # Vary the delay for realism

    # Get fully loaded HTML
    html_content = driver.page_source

    # Save the HTML for debugging
    with open(f"coches_net_rendered_{page}.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"✅ Page {page} saved!")

    # Parse the updated HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract car links
    links = soup.find_all("a", class_="mt-CardAd-media")
    links_href = [f"https://www.coches.net{link.get('href')}" for link in links if link.get("href")]

    print(f"🔗 Extracted {len(links_href)} car links")
    print(links)

driver.quit()  # Close browser session
print("✅ Scraping complete.")
