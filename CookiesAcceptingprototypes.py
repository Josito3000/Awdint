try:
    # Find the cookie banner accept button by XPath
    cookie_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Aceptar y cerrar')]")
    cookie_button.click()
    print("✅ Cookies accepted.")
    time.sleep(2)  # Wait a moment after clicking
except Exception as e:
    print("⚠ No cookie button found or already accepted.")

# **Accept Cookies using TAB + ENTER**
for _ in range(5):  # Press TAB 5 times
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB)
    time.sleep(0.2)  # Small delay to mimic human behavior

driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
print("✅ Cookies accepted.")

if page % restart_every == 0:  # Restart every 20 pages
            print("🔄 Restarting browser session to avoid detection...")
            driver.quit()
            time.sleep(1)  # Wait before reopening
            driver = uc.Chrome(options=options)
