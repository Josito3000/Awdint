import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random

# Configure Undetected Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Evade bot detection
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Launch Undetected Chrome
driver = uc.Chrome(options=chrome_options)

try:
    # Target website
    URL = "https://www.coches.net/segunda-mano/"
    driver.get(URL)

    # Wait for JavaScript to load (adjust as needed)
    time.sleep(random.uniform(100, 150))

    # Extract car prices
    prices = driver.find_elements(By.CSS_SELECTOR, "h5.mt-TitleBasic-title.mt-TitleBasic-title--xs.mt-TitleBasic-title--currentColor")

    # Print extracted prices
    for price in prices:
        print("💰 Price:", price.text)

    # Save the page source (for debugging)
    with open("coches_net_scraped.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)

    print("✅ HTML content saved.")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    driver.quit()
