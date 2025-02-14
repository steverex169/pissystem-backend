# # import random
# # import time
# # import requests
# # from datetime import datetime, timedelta
# # from playwright.sync_api import sync_playwright
# # from playwright_stealth import stealth_sync
from bs4 import BeautifulSoup
# # from selenium.webdriver.chrome.options import Options
import os
import sys

# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)  # Add the project root to sys.path

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psi-system.settings")

# Initialize Django
import django
django.setup()

# Now import models
from organizationdata.models import ScrapBetwarVolumn



# # class PartnerVolume:
#     # def __init__(self, username, password, base_url="https://betwar.com"):
#     #     # Proxy and login details
#     #     self.proxy_list_url = "https://proxy.webshare.io/api/v2/proxy/list/download/iouqvorexpcubufvlewcywrxypybuwottjggjjth/-/any/username/direct/-/"
#     #     self.proxy_user = "dtnvyuji"
#     #     self.proxy_password = "pm5um6w7spc4"
#     #     self.username = username
#     #     self.password = password
#     #     self.base_url = base_url
# #         self.proxy_host = None
# #         self.proxy_port = None
# #         self.proxy_url = None
# #         self.partners_to_select = ["PARIS", "POPE", "POPE2", "BAWS", "JCCCS", "MIZ", "CLASSICO", "JRS", "BASS"]
# #         self.date_ranges = self.generate_weekly_ranges("1/27/2025", 3)
# #         options = Options()
# #         options.add_argument("--headless")
# #         options.add_argument("--no-sandbox")
# #         options.add_argument("--disable-dev-shm-usage")
# #         options.add_argument("--disable-gpu")
# #         options.add_argument("--window-size=1920,1080")
# #         options.add_argument("--disable-blink-features=AutomationControlled")
#         # self.all_rows_data = []

# #     def fetch_proxies(self):
# #         response = requests.get(self.proxy_list_url)
# #         proxy_list = response.text.strip().split("\n")
# #         if not proxy_list:
# #             raise Exception("No proxies fetched from the provided Webshare link.")
# #         return proxy_list

# #     def get_random_proxy(self, proxy_list):
# #         proxy = random.choice(proxy_list)
# #         self.proxy_host, self.proxy_port = proxy.split(":")[:2]
# #         self.proxy_url = f"http://{self.proxy_user}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}"

# #     def verify_proxy(self):
# #         proxies = {"http": self.proxy_url, "https": self.proxy_url}
# #         headers = {
# #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
# #             "Accept-Language": "en-US,en;q=0.9",
# #             "Referer": "https://google.com",
# #             "Connection": "keep-alive",
# #         }
# #         try:
# #             ip_response = requests.get("https://ipinfo.io/json", proxies=proxies, headers=headers, timeout=10)
# #             ip_response.raise_for_status()
# #             ip_data = ip_response.json()
# #             print("Proxy verification result:")
# #             print(f"Public IP: {ip_data.get('ip')}")
# #             print(f"Location: {ip_data.get('city')}, {ip_data.get('region')}, {ip_data.get('country')}")
# #         except requests.exceptions.RequestException:
# #             print("Proxy verification failed.")
# #             raise SystemExit("Exiting script due to proxy verification failure.")

# #     def generate_weekly_ranges(self, start_date: str, weeks: int):
# #         date_format = "%m/%d/%Y"
# #         start = datetime.strptime(start_date, date_format)
# #         date_ranges = [(start.strftime(date_format), (start + timedelta(days=6)).strftime(date_format))]

# #         for _ in range(weeks - 1):
# #             start += timedelta(days=7)  # Move to the next week
# #             end_date = start + timedelta(days=6)  # End date is 6 days after the new start
# #             date_ranges.append((start.strftime(date_format), end_date.strftime(date_format)))

# #         return date_ranges

# #     def login(self):
# #         with sync_playwright() as p:
# #             browser = p.chromium.launch(headless=False, proxy={
# #                 "server": f"http://{self.proxy_host}:{self.proxy_port}",
# #                 "username": self.proxy_user,
# #                 "password": self.proxy_password
# #             })
# #             context = browser.new_context()
# #             stealth_sync(context)
# #             self.page = context.new_page()  # Store page in self.page
# #             self.page.goto(f"{self.base_url}/Logins/039/sites/betwar/index.aspx", timeout=60000)
# #             time.sleep(random.uniform(2, 5))
# #             self.page.fill("#txtAccessOfCode", self.username)
# #             self.page.fill("#txtAccessOfPassword", self.password)
# #             time.sleep(random.uniform(1, 3))
# #             self.page.click("input[type='submit']")
# #             print("Login successful.")
# #             time.sleep(random.uniform(2, 5))

# #             self.process_partners(self.page)  # Call processing function

# #     def scrape_total_volume(self, partner, page):
# #         """Scrapes only the Total Volume row for the partner."""
# #         try:
# #             total_volume_element = page.locator("//tr[@class='rowTotal']/td[6]/span")
# #             total_volume_element.wait_for(state="visible", timeout=5000)
# #             total_volume = total_volume_element.text_content().strip()
# #             print(f"{partner}: {total_volume}")
# #             return total_volume

# #         except Exception as e:
# #             print(f"⚠️ Error scraping total volume for {partner}: {e}")


#     # def scrape_performance_table(self, page, partner, date_range, total_volume):
#     #     all_rows_data = []  
#     #     try:
#     #         html = page.content()
#     #         soup = BeautifulSoup(html, "html.parser")
            
#     #         total_row = soup.find("tr", {"class": "rowTotal"})
            
#     #         if total_row:
#     #             cells = total_row.find_all("td")
#     #             if len(cells) >= 6: 
#     #                 total_volume = cells[5].text.strip()
                    
#     #                 existing_entry = next(
#     #                     (entry for entry in all_rows_data 
#     #                     if entry["partnername"] == partner 
#     #                     and entry["daterange"] == date_range),
#     #                     None
#     #                 )
                    
#     #                 if not existing_entry:
#     #                     all_rows_data.append({
#     #                         "partnername": partner,
#     #                         "daterange": date_range,
#     #                         "totalvolume": total_volume
#     #                     })
#     #                     print(f"✅ Added unique entry for {partner} - {date_range}")
#     #                 else:
#     #                     print(f"⚠️ Duplicate skipped for {partner} - {date_range}")
#     #             else:
#     #                 print(f"⚠️ Not enough cells in total row for {partner}")
#     #         else:
#     #             print(f"⚠️ Total row not found for {partner}")

#     #         print("📊 Final Clean Data:")
#     #         for entry in all_rows_data:
#     #             print(f"Partner: {entry['partnername']} | Date Range: {entry['daterange']} | Total: {entry['totalvolume']}")
                
#     #     except Exception as e:
#     #         print(f"⚠️ Error in processing {partner}: {str(e)}")

# #     def process_partners(self, page):
# #         for partner in self.partners_to_select:
# #             try:
# #                 page.goto(f"{self.base_url}/Agent/Home.aspx", wait_until="networkidle")
# #                 time.sleep(3)

# #                 # Click the dropdown button
# #                 dropdown_button = page.locator("xpath=/html/body/form/header/nav/div/div[2]/div/div/nav/div[1]/div[1]/div[2]/div/div/div/button")
# #                 dropdown_button.wait_for(state="visible", timeout=5000)
# #                 dropdown_button.click()
# #                 time.sleep(2)

# #                 # Click "Show Tree" button if visible
# #                 show_tree_button = page.locator(".btn-showtree")
# #                 if show_tree_button.is_visible():
# #                     show_tree_button.click()
# #                     time.sleep(3)

# #                 # Get the dropdown select element
# #                 select_element = page.locator(".cbo-agentList")
# #                 select_element.wait_for(state="visible", timeout=5000)

# #                 # Get all available options
# #                 available_partners = select_element.locator("option").all_text_contents()
# #                 available_partners = [opt.strip() for opt in available_partners if opt.strip()]

# #                 # Check if the partner exists
# #                 matching_option = next((opt for opt in available_partners if partner.lower() in opt.lower()), None)
# #                 if matching_option:
# #                     select_element.select_option(label=matching_option)
# #                     print(f"✅ Successfully selected: {matching_option}")

# #                     # Wait for dropdown selection effect
# #                     page.wait_for_timeout(3000)

# #                     # Wait for the page to settle before moving
# #                     page.wait_for_load_state("networkidle")

# #                     # **Fix: Check if the page has changed before navigating**
# #                     if page.url != f"{self.base_url}/Agent/CustomerPerfomanceAgent.aspx":
# #                         page.goto(f"{self.base_url}/Agent/CustomerPerfomanceAgent.aspx", wait_until="domcontentloaded")
# #                         time.sleep(3)

# #                     # Set date range
# #                     date_from, date_to = self.date_ranges[0]
# #                     total_volume = self.scrape_total_volume(partner, page)
                        
# #                     try:
# #                         # Set 'From Date'
# #                         from_date_input = page.locator("#ctl00_cphWorkArea_dtpDateFrom_dateInput")
# #                         from_date_input.wait_for(state="visible", timeout=5000)
# #                         from_date_input.click()
# #                         from_date_input.fill(date_from)
# #                         to_date_input.enter()

# #                         # Set 'To Date'
# #                         to_date_input = page.locator("#ctl00_cphWorkArea_dtpDateTo_dateInput")
# #                         to_date_input.wait_for(state="visible", timeout=5000)
# #                         to_date_input.click()
# #                         to_date_input.fill(date_to)
# #                         to_date_input.enter()

# #                         # Wait for the page to update or some element to indicate the date filter applied
# #                         page.locator("selector-for-updated-element").wait_for(state="visible", timeout=10000)  # Replace with actual selector
                        
# #                         print(f"📅 Selected date range: {date_from} to {date_to}")

# #                         # Ensure the page has fully loaded after applying the date range filter
# #                         page.wait_for_load_state("networkidle")
                        
# #                         # Call scraping functions
# #                         self.scrape_total_volume(partner, page)
# #                         self.scrape_performance_table(page, partner, f"{date_from} to {date_to}", total_volume)

# #                     except Exception as e:
# #                         print(f"⚠️ Error setting date range: {e}")


# #                 else:
# #                     print(f"❌ Partner {partner} not found in the dropdown.")

# #             except Exception as e:
# #                 print(f"⚠️ Error processing partner {partner}: {e}")
        
# #         print("🎯 Process completed successfully.")
# #     def close(self):
# #         print("Closing resources")


# # if __name__ == "__main__":
# #     scraper = PartnerVolume(
# #         username="spades",
# #         password="yoguy$",
# #         base_url="https://betwar.com"
# #     )
# #     proxy_list = scraper.fetch_proxies()
# #     scraper.get_random_proxy(proxy_list)
# #     scraper.verify_proxy()
# #     scraper.login()
# #     scraper.close()





# from datetime import datetime, timedelta
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# import time
# from bs4 import BeautifulSoup  # Ensure you have BeautifulSoup installed: `pip install beautifulsoup4`

# class PartnerVolume:
#     def __init__(self, username, password, base_url="https://betwar.com"):  # ✅ FIXED INIT
#         self.email = username
#         self.password = password
#         self.base_url = base_url
#         options = Options()
#         options.add_argument("--headless")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-gpu")
#         options.add_argument("--window-size=1920,1080")
#         options.add_argument("--disable-blink-features=AutomationControlled")

#         # Extra settings
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)

#         # Initialize Chrome WebDriver
#         service = Service(ChromeDriverManager().install())
#         self.driver = webdriver.Chrome(service=service, options=options)

#         # Set timeouts
#         self.driver.set_page_load_timeout(60)
#         self.driver.implicitly_wait(20)

#         # Initialize WebDriverWait
#         self.wait = WebDriverWait(self.driver, 20)

#         self.partners_to_select = ["POPE2"]
#         self.date_ranges = self.generate_weekly_ranges("1/20/2025", 3)
#         print("✅ WebDriver initialized successfully.")
#         self.all_rows_data = []

#     def generate_weekly_ranges(self, start_date: str, weeks: int):
#         date_format = "%m/%d/%Y"
#         start = datetime.strptime(start_date, date_format)
#         date_ranges = [(start.strftime(date_format), (start + timedelta(days=6)).strftime(date_format))]
#         for _ in range(weeks - 1):
#             start += timedelta(days=7)
#             date_ranges.append((start.strftime(date_format), (start + timedelta(days=6)).strftime(date_format)))
#         return date_ranges

#     def login(self):
#         self.driver.get(f"{self.base_url}/Logins/039/sites/betwar/index.aspx")
#         time.sleep(2)

#         try:
#             username_field = self.wait.until(EC.presence_of_element_located((By.ID, "txtAccessOfCode")))
#             username_field.send_keys(self.email)
#             print("✅ Username entered.")

#             password_field = self.wait.until(EC.presence_of_element_located((By.ID, "txtAccessOfPassword")))
#             password_field.send_keys(self.password)
#             print("✅ Password entered.")

#             login_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn01")))
#             login_button.click()
#             print("✅ Login button clicked.")

#             time.sleep(5)  # Allow time for page to load after login

#         except Exception as e:
#             print(f"⚠ Login error: {e}")

#     def scrape_total_volume(self, partner):
#         """Scrapes only the Total Volume row for the partner."""
#         try:
#             total_volume_element = self.wait.until(
#                 EC.presence_of_element_located((By.XPATH, "//tr[@class='rowTotal']/td[6]/span"))
#             )
#             total_volume = total_volume_element.text.strip()
#             print(f"{partner}: {total_volume}")
#         except Exception as e:
#             print(f"⚠ Error scraping total volume for {partner}: {e}")

#     def scrape_performance_table(self, partner, date_range):
#         all_rows_data = []
#         try:
#             html = self.driver.page_source
#             soup = BeautifulSoup(html, "html.parser")

#             total_row = soup.find("tr", {"class": "rowTotal"})

#             if total_row:
#                 cells = total_row.find_all("td")
#                 if len(cells) >= 6:
#                     total_volume = cells[5].text.strip()

#                     existing_entry = next(
#                         (entry for entry in all_rows_data
#                          if entry["partnername"] == partner
#                          and entry["daterange"] == date_range),
#                         None
#                     )

#                     if not existing_entry:
#                         all_rows_data.append({
#                             "partnername": partner,
#                             "daterange": date_range,
#                             "totalvolume": total_volume
#                         })
#                         print(f"✅ Added unique entry for {partner} - {date_range}")
#                     else:
#                         print(f"⚠ Duplicate skipped for {partner} - {date_range}")
#                 else:
#                     print(f"⚠ Not enough cells in total row for {partner}")
#             else:
#                 print(f"⚠ Total row not found for {partner}")

#             print("📊 Final Clean Data:")
#             for entry in all_rows_data:
#                 print(f"Partner: {entry['partnername']} | Date Range: {entry['daterange']} | Total: {entry['totalvolume']}")

#         except Exception as e:
#             print(f"⚠ Error in processing {partner}: {str(e)}")

#     def process_partners(self):
#         for partner in self.partners_to_select:
#             try:
#                 self.driver.get("https://www.betwar.com/Agent/Home.aspx")
#                 time.sleep(3)
#                 dropdown_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,
#                                                                               "/html/body/form/header/nav/div/div[2]/div/div/nav/div[1]/div[1]/div[2]/div/div/div/button")))
#                 self.driver.execute_script("arguments[0].click();", dropdown_button)
#                 show_tree_button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-showtree")))
#                 self.driver.execute_script("arguments[0].click();", show_tree_button)
#                 time.sleep(3)
#                 select_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "cbo-agentList")))
#                 select = Select(select_element)
#                 available_partners = [option.text.strip() for option in select.options if option.text.strip()]
#                 matching_option = next((opt for opt in available_partners if partner.lower() in opt.lower()), None)
#                 if matching_option:
#                     select.select_by_visible_text(matching_option)
#                     print(f"✅ Successfully selected: {matching_option}")
#                     self.driver.get("https://www.betwar.com/Agent/CustomerPerfomanceAgent.aspx")
#                     time.sleep(3)
#                     date_from, date_to = self.date_ranges[0]
#                     try:
#                         from_date_input = self.wait.until(
#                             EC.presence_of_element_located((By.ID, "ctl00_cphWorkArea_dtpDateFrom_dateInput")))
#                         self.driver.execute_script("arguments[0].setAttribute('value', arguments[1])", from_date_input,
#                                                    date_from)
#                         from_date_input.send_keys(Keys.ENTER)
#                         time.sleep(2)
#                         to_date_input = self.wait.until(
#                             EC.presence_of_element_located((By.ID, "ctl00_cphWorkArea_dtpDateTo_dateInput")))
#                         self.driver.execute_script("arguments[0].setAttribute('value', arguments[1])", to_date_input,
#                                                    date_to)
#                         to_date_input.send_keys(Keys.ENTER)
#                         print(f"📅 Selected date range: {date_from} to {date_to}")
#                         time.sleep(5)
#                         self.scrape_total_volume(partner)
#                     except Exception as e:
#                         print(f"⚠ Error setting date range: {e}")
#                 else:
#                     print(f"❌ Partner {partner} not found in the dropdown.")
#             except Exception as e:
#                 print(f"⚠ Error processing partner {partner}: {e}")
#         print("🎯 Process completed successfully.")

#     def close(self):
#         self.driver.quit()

# if __name__ == "__main__":  # ✅ FIXED NAME CHECK
    # scraper = PartnerVolume(
    #     username="spades",
    #     password="yoguy$",
    #     base_url="https://betwar.com"
    # )
#     scraper.login()
#     scraper.process_partners()
#     input("\n🔴 Press ENTER to exit the script...")
#     scraper.close()





# from playwright.sync_api import sync_playwright
# from datetime import datetime, timedelta
# from bs4 import BeautifulSoup
# from organizationdata.models import ScrapBetwarVolumn
# from django.db import connection
# from asgiref.sync import sync_to_async
# import time

# class PartnerVolume:
#     def __init__(self, username, password, base_url="https://betwar.com"):
#         self.username = username
#         self.password = password
#         self.base_url = base_url
#         self.playwright = sync_playwright().start()
#         self.browser = self.playwright.chromium.launch(headless=True)
#         self.context = self.browser.new_context()
#         self.page = self.context.new_page()
#         self.partners_to_select = ["POPE2", "POPE", "BASS", "JRS", "CLASSICO", "MIZ", "JCCCS", "BAWS", "PARIS"]
#         self.date_ranges = self.generate_weekly_ranges("1/20/2025", 3)

#     def generate_weekly_ranges(self, start_date: str, weeks: int):
#         date_format = "%m/%d/%Y"
#         start = datetime.strptime(start_date, date_format)
#         date_ranges = [(start.strftime(date_format), (start + timedelta(days=6)).strftime(date_format))]
#         for _ in range(weeks - 1):
#             start += timedelta(days=7)
#             date_ranges.append((start.strftime(date_format), (start + timedelta(days=6)).strftime(date_format)))
#         return date_ranges

#     def login(self):
#         try:
#             self.page.goto("https://www.betwar.com/Logins/039/sites/betwar/index.aspx", timeout=60000)
#             self.page.wait_for_load_state("domcontentloaded")
#             self.page.wait_for_selector("#txtAccessOfCode", timeout=15000)
#             self.page.wait_for_selector("#txtAccessOfPassword", timeout=15000)
#             self.page.fill("#txtAccessOfCode", self.username)
#             self.page.fill("#txtAccessOfPassword", self.password)
#             self.page.click(".btn01")
#             self.page.wait_for_load_state("networkidle")
#             print("✅ Login successful")
#         except Exception as e:
#             print(f"❌ Login failed: {e}")

#     def scrape_total_volume(self):
#         try:
#             total_volume_element = self.page.wait_for_selector("//tr[@class='rowTotal']/td[6]/span", timeout=10000)
#             return total_volume_element.inner_text().strip()
#         except Exception as e:
#             print(f"⚠️ Error scraping total volume: {e}")
#             return None

#     def process_partners(self):
#         with connection.cursor():  # Ensures Django ORM runs in sync mode
#             for partner in self.partners_to_select:
#                 try:
#                     self.page.goto("https://www.betwar.com/Agent/Home.aspx")
#                     self.page.wait_for_timeout(3000)
#                     self.page.click("xpath=/html/body/form/header/nav/div/div[2]/div/div/nav/div[1]/div[1]/div[2]/div/div/div/button")
#                     self.page.click(".btn-showtree")
#                     self.page.wait_for_timeout(3000)

#                     select_element = self.page.wait_for_selector(".cbo-agentList")
#                     available_partners = [option.inner_text().strip() for option in select_element.query_selector_all("option") if option.inner_text().strip()]

#                     matching_option = next((opt for opt in available_partners if partner.lower() in opt.lower()), None)
#                     if matching_option:
#                         self.page.select_option(".cbo-agentList", label=matching_option)
#                         print(f"✅ Selected: {matching_option}")
#                         time.sleep(5)
#                         self.page.goto("https://www.betwar.com/Agent/CustomerPerfomanceAgent.aspx")
#                         self.page.wait_for_timeout(3000)

#                         for date_from, date_to in self.date_ranges:
#                             try:
#                                 self.page.fill("#ctl00_cphWorkArea_dtpDateFrom_dateInput", date_from)
#                                 self.page.keyboard.press("Enter")
#                                 self.page.wait_for_timeout(2000)
#                                 self.page.fill("#ctl00_cphWorkArea_dtpDateTo_dateInput", date_to)
#                                 self.page.keyboard.press("Enter")
#                                 print(f"📅 Date range: {date_from} to {date_to}")
#                                 self.page.wait_for_timeout(5000)

#                                 total_volume = self.scrape_total_volume()
#                                 if total_volume:
#                                     self.save_to_db(partner, f"{date_from} to {date_to}", total_volume)
#                             except Exception as e:
#                                 print(f"⚠️ Error setting date range: {e}")
#                     else:
#                         print(f"❌ Partner {partner} not found in the dropdown.")
#                 except Exception as e:
#                     print(f"⚠️ Error processing partner {partner}: {e}")

#             print("🎯 Process completed successfully.")

#     @sync_to_async
#     def save_to_db(self, partner, date_range, volume):
#         """ Save scraped data to the database """
#         try:
#             date_parts = date_range.split(" to ")
#             if len(date_parts) == 2:
#                 start_date = datetime.strptime(date_parts[0], "%m/%d/%Y")
#                 end_date = datetime.strptime(date_parts[1], "%m/%d/%Y")
#                 formatted_date_range = f"{start_date.strftime('%-m/%-d/%y')} - {end_date.strftime('%-m/%-d/%y')}"
#             else:
#                 formatted_date_range = "N/A"

#             ScrapBetwarVolumn.objects.create(
#                 partner_name=partner,
#                 weak_date=formatted_date_range,
#                 volume=volume
#             )
#             print(f"✅ Data saved: {partner} | {formatted_date_range} | {volume}")

#         except Exception as e:
#             print(f"⚠️ Database error: {e}")

#     def close(self):
#         self.browser.close()
#         self.playwright.stop()

# if __name__ == "__main__":
#     scraper = PartnerVolume(username="spades", password="yoguy$")
#     scraper.login()
#     scraper.process_partners()
#     input("\n🔴 Press ENTER to exit the script...")
#     scraper.close()



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
import random
from fake_useragent import UserAgent

class WeeklyFigureScraper:
    def __init__(self, email, password, base_url):
        self.email = email
        self.password = password
        self.base_url = base_url
        self.driver = None
        self.scraped_data = []

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # **Add Random User-Agent**
        ua = UserAgent()
        options.add_argument(f"user-agent={ua.random}")

        # **Additional Anti-Detection Measures**
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # **Setup Chrome Driver**
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
 # **Increase Page Load Timeout**
        self.driver.set_page_load_timeout(120)
        self.driver.implicitly_wait(30)

    def safe_get(self, url, retries=3):
        """Retry logic for page loading."""
        for attempt in range(retries):
            try:
                self.driver.get(url)
                return
            except TimeoutException:
                print(f"Timeout occurred, retrying {attempt + 1}/{retries}...")
                time.sleep(5)
        raise TimeoutException("Failed to load page after multiple attempts.")

    def login(self):
        """Logs into the system using the provided credentials."""
        print("Opening login page...")
        self.safe_get(f"{self.base_url}/auth/signin")

        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "inputEmailAddress"))
        ).send_keys(self.email)
        self.driver.find_element(By.ID, "inputPassword").send_keys(self.password)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.page-inner"))
        )
    print("Login successful.")

    def navigate_to_weekly_figure(self):
        """Navigates to the Weekly Figure page and selects the previous week."""
        print("Navigating to Weekly Figure page...")
        self.safe_get(f"{self.base_url}/reports/weekly-figure/0/0/0/0/0/0/-1/-1/0/0")

        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "calendar-today"))
        )
        today_button = self.driver.find_element(By.ID, "calendar-today")
        today_text = today_button.text
        print(f"Today's date range: {today_text}")

        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "calendar-prev"))
        )
        prev_button = self.driver.find_element(By.ID, "calendar-prev")
        prev_button.click()
        time.sleep(3)
        print("Previous week selected.")

    def process_dropdowns(self):
        """Processes dropdowns efficiently with batch processing."""
        print("Navigating to Weekly Figure page...")

        try:
            dropdown_elements = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td fa-icon.ng-fa-icon"))
            )

            total_dropdowns = len(dropdown_elements)
            print(f"Total dropdowns found: {total_dropdowns}")

            for idx in range(total_dropdowns):
                try:
                    print(f"Processing dropdown {idx + 1} of {total_dropdowns}...")
                    dropdown = dropdown_elements[idx]

                    if dropdown.is_displayed() and dropdown.is_enabled():
                        partner_data = self.process_dropdown(idx + 1)
                        if partner_data and partner_data.get("dropdown_data"):
                            self.scraped_data.append(partner_data)
                        else:
                            print(f"No valid data for dropdown {idx + 1}")

                    # **Pause after every 5 dropdowns to reduce server load**
                    if (idx + 1) % 5 == 0:
                        print("Pausing for 8-12 seconds to avoid detection...")
                        time.sleep(random.uniform(8, 12))  

                except Exception as e:
                    print(f"Error processing dropdown {idx + 1}: {str(e)}")
                    continue

        except TimeoutException:
            print("Timed out waiting for dropdown elements")
        except Exception as e:
            print(f"General dropdown processing error: {str(e)}")

        return self.scraped_data
    def save_to_db_sync(self, partner):
        """Ensures database operations run synchronously."""
        try:
            for entry in partner["dropdown_data"]:
                Scrapdata.objects.create(
                    partner_name=partner['partner_name'],
                    user=partner['partner_name'],
                    total=partner['total'],
                    partner_profit=partner['today_text'],
                    office_profit=entry.get('office_profit', None),
                    website_url=entry.get('website_url', None),
                    username=entry.get('username', partner['partner_name']),
                    password=entry.get('password', ''),
                    figure=entry.get('figure', 0),
                    affiliate_profit=entry.get('affiliate_profit', 0),
                    office_profit_dropdown=entry.get('office_profit', None)
                )
        except Exception as e:
            print(f"Database error: {e}")

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

    if scraper.scraped_data:
        for partner in scraper.scraped_data:
            print(f"Partner Name: {partner['partner_name']}, Total: {partner['total']}, Today Text: {partner['today_text']}")
            for entry in partner["dropdown_data"]:
                print(f"    Website: {entry['website_url']}, Username: {entry['username']}, Password: {entry['password']}, Figure: {entry['figure']}")
    else:
	    print("No data was scraped.")

  

from playwright.async_api import async_playwright
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from organizationdata.models import ScrapBetwarVolumn
from asgiref.sync import sync_to_async
import asyncio

class PartnerVolume:
    def __init__(self, username, password, base_url="https://betwar.com"):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.partners_to_select = ["POPE2", "POPE", "BASS", "JRS", "SNOWCLASSICO", "MIZ", "JCCCS", "BAWS", "PARIS"]
        self.date_ranges = self.generate_weekly_ranges("1/20/2025", 3)

    def generate_weekly_ranges(self, start_date: str, weeks: int):
        """ Generate weekly date ranges (Monday-Sunday) """
        date_format = "%m/%d/%Y"
        start = datetime.strptime(start_date, date_format)
        date_ranges = [(start.strftime(date_format), (start + timedelta(days=6)).strftime(date_format))]
        for _ in range(weeks - 1):
            start += timedelta(days=7)
            date_ranges.append((start.strftime(date_format), (start + timedelta(days=6)).strftime(date_format)))
        return date_ranges

    async def login(self, page):
        """ Log in to the website """
        try:
            await page.goto("https://www.betwar.com/Logins/039/sites/betwar/index.aspx", timeout=60000)
            await page.wait_for_load_state("domcontentloaded")

            await page.wait_for_selector("#txtAccessOfCode", timeout=15000)
            await page.wait_for_selector("#txtAccessOfPassword", timeout=15000)

            await page.fill("#txtAccessOfCode", self.username)
            await page.fill("#txtAccessOfPassword", self.password)

            await page.click(".btn01")
            await page.wait_for_load_state("networkidle")

            print("✅ Login successful")
        except Exception as e:
            print(f"❌ Login failed: {e}")

    async def scrape_total_volume(self, page):
        """ Scrape the total volume value from the table """
        try:
            total_volume_element = await page.wait_for_selector("//tr[@class='rowTotal']/td[6]/span", timeout=10000)
            return (await total_volume_element.inner_text()).strip()
        except Exception as e:
            print(f"⚠️ Error scraping total volume: {e}")
            return None

    async def process_partners(self):
        """ Process each partner and store data """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await self.login(page)  # Perform login

            for partner in self.partners_to_select:
                try:
                    await page.goto("https://www.betwar.com/Agent/Home.aspx")
                    await asyncio.sleep(3)
                    await page.click("xpath=/html/body/form/header/nav/div/div[2]/div/div/nav/div[1]/div[1]/div[2]/div/div/div/button")
                    await page.click(".btn-showtree")
                    await asyncio.sleep(3)

                    select_element = await page.wait_for_selector(".cbo-agentList")
                    available_partners = [await option.inner_text() for option in await select_element.query_selector_all("option")]

                    matching_option = next((opt for opt in available_partners if partner.lower() in opt.lower()), None)
                    if matching_option:
                        await page.select_option(".cbo-agentList", label=matching_option)
                        print(f"✅ Selected: {matching_option}")

                        await asyncio.sleep(5)
                        await page.goto("https://www.betwar.com/Agent/CustomerPerfomanceAgent.aspx")
                        await asyncio.sleep(3)

                        for date_from, date_to in self.date_ranges:
                            if (datetime.strptime(date_to, "%m/%d/%Y") - datetime.strptime(date_from, "%m/%d/%Y")).days == 6:
                                try:
                                    await page.fill("#ctl00_cphWorkArea_dtpDateFrom_dateInput", date_from)
                                    await page.keyboard.press("Enter")
                                    await asyncio.sleep(2)
                                    await page.fill("#ctl00_cphWorkArea_dtpDateTo_dateInput", date_to)
                                    await page.keyboard.press("Enter")
                                    print(f"📅 Date range: {date_from} to {date_to}")
                                    await asyncio.sleep(5)

                                    total_volume = await self.scrape_total_volume(page)
                                    if total_volume:
                                        await self.save_to_db(partner, f"{date_from} to {date_to}", total_volume)

                                except Exception as e:
                                    print(f"⚠️ Error setting date range: {e}")
                            else:
                                print(f"❌ Skipping date range {date_from} to {date_to} (not exactly 6 days apart)")

                    else:
                        print(f"❌ Partner {partner} not found in the dropdown.")
                except Exception as e:
                    print(f"⚠️ Error processing partner {partner}: {e}")

            await browser.close()
            print("🎯 Process completed successfully.")

    def save_to_db_sync(self, partner, date_range, volume):
        """ Synchronous function to save scraped data to the database """
        try:
            date_parts = date_range.split(" to ")
            if len(date_parts) == 2:
                start_date = datetime.strptime(date_parts[0], "%m/%d/%Y")
                end_date = datetime.strptime(date_parts[1], "%m/%d/%Y")
                formatted_date_range = f"{start_date.strftime('%-m/%-d/%y')} - {end_date.strftime('%-m/%-d/%y')}"
            else:
                formatted_date_range = "N/A"

            ScrapBetwarVolumn.objects.create(
                partner_name=partner,
                weak_date=formatted_date_range,
                volume=volume
            )
            print(f"✅ Data saved: {partner} | {formatted_date_range} | {volume}")

        except Exception as e:
            print(f"⚠️ Database error: {e}")

    async def save_to_db(self, partner, date_range, volume):
        """ Async wrapper to call sync DB function """
        await sync_to_async(self.save_to_db_sync, thread_sensitive=True)(partner, date_range, volume)

if __name__ == "__main__":
    scraper = PartnerVolume(username="spades", password="yoguy$", base_url="https://betwar.com")
    asyncio.run(scraper.process_partners())  # Correct way to run async functions
