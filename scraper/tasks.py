from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up Chrome options and driver
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Use WebDriver Manager to handle driver setup
driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=options)

try:
    # Maximize the browser window
    driver.maximize_window()

    # Navigate to the login page
    driver.get("https://betwar.com/Logins/039/sites/betwar/index.aspx")

    # Locate and fill in the username and password fields
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "txtAccessOfCode"))
    )
    driver.find_element(By.ID, "txtAccessOfCode").send_keys("spades")
    driver.find_element(By.ID, "txtAccessOfPassword").send_keys("yoguy2")

    # Click the submit button
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    print("Login successful.")

    # Navigate to the 'Daily Figures' page after login
    driver.get("https://betwar.com/Agent/DailyFigures.aspx")
    print("Navigated to the Daily Figures page.")

    # Wait for the 'Last Week' button to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "btnWeek2"))
    )

    # Click the 'Last Week' button
    driver.find_element(By.ID, "btnWeek2").click()
    print("Clicked the 'Last Week' button.")

    # Wait for the table to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "tblfigure"))
    )

    # Scrape the table
    table = driver.find_element(By.ID, "tblfigure")
    rows = table.find_elements(By.TAG_NAME, "tr")

    print("Scraping table data...")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        data = [cell.text for cell in cells]
        print(data)

    # Pause to inspect or modify after scraping
    input("Press Enter to continue after reviewing the scraped data...")

finally:
    # Close the browser
    driver.quit()
from celery import shared_task
import requests

@shared_task
def scrape_and_post_data():
    api_url = "http://127.0.0.1:8000/api/scraper/scrape-weekly-figures-betwar/"  # Replace with your API endpoint
    payload = {
        "username": "spades",
        "password": "yoguy2",
        "base_url": "https://betwar.com"
    }
    try:
        response = requests.post(api_url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
