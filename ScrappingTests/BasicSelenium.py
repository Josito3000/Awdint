import time
import undetected_chromedriver as uc

# Launch undetected Chrome
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
options.add_argument("start-maximized")  # Open full screen like a real user
options.add_argument("--disable-extensions")  # Mimic a clean browser
options.add_argument("--incognito")  # Use incognito mode to prevent tracking

# Start Chrome using undetected-chromedriver
driver = uc.Chrome(options=options)

url = "https://www.coches.net"
driver.get(url)

# Keep browser open for inspection
print("✅ Browser launched. Press Enter to close.")
input()

# Close the browser
driver.quit()
