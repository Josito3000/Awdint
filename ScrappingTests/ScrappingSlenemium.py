from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configure Selenium with Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run without opening a browser (remove if debugging)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Start the browser
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load the page
URL = "https://www.coches.net/segunda-mano/"
driver.get(URL)

# Wait for JavaScript to load
time.sleep(5)

# Get the updated page source
html = driver.page_source

# Save the content
with open("coches_net_selenium.html", "w", encoding="utf-8") as file:
    file.write(html)

print("✅ HTML content saved using Selenium.")

# Close browser
driver.quit()
