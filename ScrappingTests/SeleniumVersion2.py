from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configure Selenium
chrome_options = Options()
# REMOVE "--headless" to avoid bot detection
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Helps evade detection
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Start the browser in normal mode
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the site and wait for manual interaction
URL = "https://www.coches.net/segunda-mano/"
driver.get(URL)

input("🔴 Solve any CAPTCHA manually and then press Enter...")

# Save the session's HTML after manual validation
time.sleep(5)
html = driver.page_source

with open("coches_net_selenium_manual.html", "w", encoding="utf-8") as file:
    file.write(html)

print("✅ Saved HTML after manual verification.")
driver.quit()
