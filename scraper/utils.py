import os
import sys
from datetime import datetime

# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)  # Add the project root to sys.path

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psi-system.settings")

# Initialize Django
import django
django.setup()

# Now import models
from organizationdata.models import Scrapdata

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

import time

class WeeklyFigureScraper:
    def __init__(self, email, password, base_url):
        self.email = email
        self.password = password
        self.base_url = base_url
        self.driver = None
        self.scraped_data = []
        self.scraped_data = []

    def setup_driver(self):
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # اضافی سیٹنگز
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # ChromeDriverManager کو اپ ڈیٹ کریں
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # ٹائم آؤٹ سیٹ کریں
        self.driver.set_page_load_timeout(60)
        self.driver.implicitly_wait(20)

    def login(self):
        """Logs into the system using the provided credentials."""
        print("Opening login page...")
        self.driver.get(f"{self.base_url}/auth/signin")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "inputEmailAddress"))
        ).send_keys(self.email)
        self.driver.find_element(By.ID, "inputPassword").send_keys(self.password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.page-inner"))
        )
        print("Login successful.")

    def navigate_to_weekly_figure(self):
        """Navigates to the Weekly Figure page and selects the previous week."""
        print("Navigating to Weekly Figure page...")
        self.driver.get(f"{self.base_url}/reports/weekly-figure/0/0/0/0/0/0/-1/-1/0/0")

        # Wait for the page to load completely
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "calendar-today"))
        )

        today_button = self.driver.find_element(By.ID, "calendar-today")
        today_text = today_button.text
        print(f"Today's date range: {today_text}")

        print("Waiting for overlay to disappear...")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "overlay"))
            )
            print("Overlay disappeared, proceeding with click.")
        except TimeoutException:
            print("Overlay did not disappear in time, attempting forced click...")

        # Locate the "calendar-prev" button
        prev_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "calendar-prev"))
        )

        print("Selecting previous week...")
        self.driver.execute_script("arguments[0].click();", prev_button)  # Force JavaScript click
        time.sleep(2)
        print("Previous week selected.")

    from datetime import datetime

    def format_today_text(today_text):
        """Converts date range from '2/3/25 - 2/9/25' to '02/03/25 - 02/09/25'."""
        try:
            start_date, end_date = today_text.split(" - ")
            formatted_start = datetime.strptime(start_date, '%m/%d/%y').strftime('%m/%d/%y')
            formatted_end = datetime.strptime(end_date, '%m/%d/%y').strftime('%m/%d/%y')
            return f"{formatted_start} - {formatted_end}"
        except ValueError:
            return today_text  # If parsing fails, return as is

    def process_dropdowns(self):
        """Processes dropdowns more efficiently."""
        try:
            # Wait for all dropdown elements to be visible
            dropdown_elements = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td fa-icon.ng-fa-icon"))
            )
            
            total_dropdowns = len(dropdown_elements)
            print(f"Total dropdowns found: {total_dropdowns}")
            
            # Process each dropdown
            for idx in range(total_dropdowns):
                try:
                    print(f"Processing dropdown {idx + 1} of {total_dropdowns}...")
                    
                    # Check if the dropdown is displayed and enabled
                    dropdown = dropdown_elements[idx]
                    if dropdown.is_displayed() and dropdown.is_enabled():
                        partner_data = self.process_dropdown(idx + 1)
                        
                        # Append valid partner data to the scraped data list
                        if partner_data and partner_data.get("dropdown_data"):
                            self.scraped_data.append(partner_data)
                        else:
                            print(f"No valid data for dropdown {idx + 1}")
                    
                    # Sleep for 5 seconds every 10 dropdowns to avoid overloading the server
                    if (idx + 1) % 10 == 0:
                        print("Pausing for 5 seconds after 10 dropdowns...")
                        time.sleep(5)
                            
                except Exception as e:
                    print(f"Error processing dropdown {idx + 1}: {str(e)}")
                    continue
                    
        except TimeoutException:
            print("Timed out waiting for dropdown elements")
        except Exception as e:
            print(f"General dropdown processing error: {str(e)}")
        
        return self.scraped_data

    def process_dropdown(self, dropdown_index):
        """Processes a single dropdown and extracts its data."""
        # Locate parent row to get the partner name and summary data
        try:
            parent_row = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"(//td/fa-icon)[{dropdown_index}]/ancestor::tr"))
            )
            parent_cols = parent_row.find_elements(By.TAG_NAME, "td")
            parent_row = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"(//td/fa-icon)[{dropdown_index}]/ancestor::tr"))
            )
            today_button = self.driver.find_element(By.ID, "calendar-today")
            today_text = today_button.text
            partner_name = parent_cols[1].text.strip() if parent_cols[1].text.strip() else ""  # Partner name
            total = parent_cols[2].text.strip() if parent_cols[2].text.strip() else ""  # Total
            partner_profit = parent_cols[3].text.strip() if parent_cols[3].text.strip() else ""  # Partner profit
            office_profit = parent_cols[4].text.strip() if parent_cols[4].text.strip() else ""  # Office profit

            # print(f"Partner: {partner_name}, Total: {total}, Partner Profit: {partner_profit}, Office Profit: {office_profit}")

            # Initialize partner data dictionary
            partner_data = {
                "partner_name": partner_name,
                "total": total,
                "partner_profit": partner_profit,
                "office_profit": office_profit,
                "today_text": today_text,  # This is the key update here
                "dropdown_data": []  # Initialize dropdown data as empty list
            }

            # Locate and click the dropdown
            dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"(//td/fa-icon)[{dropdown_index}]"))
            )
            dropdown.click()

            # Wait for the table to appear
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"(//td/fa-icon)[{dropdown_index}]/ancestor::tr/following-sibling::tr/td/table"))
            )

            # Scrape expanded dropdown table rows
            rows = table.find_elements(By.TAG_NAME, "tr")
            if rows:
                for row in rows[1:]:  # Skip the header row
                    cols = row.find_elements(By.TAG_NAME, "td")
                    row_data = {
                        "website_url": cols[0].text.strip() if cols[0].text.strip() else "",
                        "username": cols[1].text.strip() if cols[1].text.strip() else "",
                        "password": cols[2].text.strip() if cols[2].text.strip() else "",
                        "figure": cols[3].text.strip() if cols[3].text.strip() else "",
                        "affiliate_profit": cols[4].text.strip() if cols[4].text.strip() else "",
                        "office_profit": cols[5].text.strip() if cols[5].text.strip() else "",
                        "today_text": cols[6].text.strip() if len(cols) > 6 else 'N/A'  # Safeguard if there's no date text
                    }
                   
                    # print(f"    Website: {row_data['website_url']}, Username: {row_data['username']}, Password: {row_data['password']}, "
                    #     f"Figure: {row_data['figure']}, Affiliate Profit: {row_data['affiliate_profit']}, Office Profit: {row_data['office_profit']}")
                    # Append row data to dropdown_data
                    partner_data["dropdown_data"].append(row_data)
                    # print(f"Appending row data: {row_data}")
            else:
                print(f"No rows found for dropdown {dropdown_index}, skipping.")

            # After processing dropdown, append partner data to scraped_data
            self.scraped_data.append(partner_data)
            # print(f"Appending partner data: {partner_data}")

            # Collapse the dropdown after processing
            dropdown.click()
            time.sleep(2)  # Allow DOM to stabilize before moving to the next dropdown

        except Exception as e:
            print(f"Error processing dropdown {dropdown_index}: {e}")

        return partner_data

    def close(self):
        """Closes the WebDriver."""
        if self.driver:
            self.driver.quit()
            print("Browser closed.")

if __name__ == "__main__":
    scraper = WeeklyFigureScraper(
        email="jtinplay5",
        password="InPlay5",
        base_url="http://72.52.240.29:9000"
    )

    try:
        scraper.setup_driver()
        scraper.login()
        scraper.navigate_to_weekly_figure()
        scraper.process_dropdowns()

    finally:
        scraper.close()

    # Final check of the scraped data
    if scraper.scraped_data:
        # print("Final Scraped Data:")
        for partner in scraper.scraped_data:
            print(f"Partner Name: {partner['partner_name']}, Total: {partner['total']}, Today Text: {partner['today_text']}, ")
            for entry in partner["dropdown_data"]:
                print(f"    Website: {entry['website_url']}, Username: {entry['username']}, "
                    f"Password: {entry['password']}, Today Text: {entry['today_text']}, Figure: {entry['figure']}")
                try:
                    Scrapdata.objects.create(
                        partner_name=partner['partner_name'],
                        user=partner['partner_name'],
                        total=partner['total'],
                        partner_profit=partner['today_text'],
                        office_profit=entry.get('office_profit', None),
                        website_url=entry.get('website_url', None),
                        username=entry.get('username', partner['partner_name']),
                        password=entry.get('password', entry.get('username', '')),
                        figure=entry.get('figure', 0),
                        affiliate_profit=entry.get('affiliate_profit', 0),
                        office_profit_dropdown=entry.get('office_profit', None)
                    )
                    print(f"✅ Data saved for {partner['partner_name']}")
                except Exception as e:
                    print(f"❌ Error saving data: {str(e)}")

    else:
        print("No data was scraped.")
