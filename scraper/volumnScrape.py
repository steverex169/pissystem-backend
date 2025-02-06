import random
import time
import requests
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options



class PartnerVolume:
    def __init__(self, username, password, base_url="https://betwar.com"):
        # Proxy and login details
        self.proxy_list_url = "https://proxy.webshare.io/api/v2/proxy/list/download/iouqvorexpcubufvlewcywrxypybuwottjggjjth/-/any/username/direct/-/"
        self.proxy_user = "dtnvyuji"
        self.proxy_password = "pm5um6w7spc4"
        self.username = username
        self.password = password
        self.base_url = base_url
        self.proxy_host = None
        self.proxy_port = None
        self.proxy_url = None
        self.partners_to_select = ["PARIS", "POPE", "POPE2", "BAWS", "JCCCS", "MIZ", "CLASSICO", "JRS", "BASS"]
        self.date_ranges = self.generate_weekly_ranges("1/20/2025", 3)
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.all_rows_data = []

    def fetch_proxies(self):
        response = requests.get(self.proxy_list_url)
        proxy_list = response.text.strip().split("\n")
        if not proxy_list:
            raise Exception("No proxies fetched from the provided Webshare link.")
        return proxy_list

    def get_random_proxy(self, proxy_list):
        proxy = random.choice(proxy_list)
        self.proxy_host, self.proxy_port = proxy.split(":")[:2]
        self.proxy_url = f"http://{self.proxy_user}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}"

    def verify_proxy(self):
        proxies = {"http": self.proxy_url, "https": self.proxy_url}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://google.com",
            "Connection": "keep-alive",
        }
        try:
            ip_response = requests.get("https://ipinfo.io/json", proxies=proxies, headers=headers, timeout=10)
            ip_response.raise_for_status()
            ip_data = ip_response.json()
            print("Proxy verification result:")
            print(f"Public IP: {ip_data.get('ip')}")
            print(f"Location: {ip_data.get('city')}, {ip_data.get('region')}, {ip_data.get('country')}")
        except requests.exceptions.RequestException:
            print("Proxy verification failed.")
            raise SystemExit("Exiting script due to proxy verification failure.")

    def generate_weekly_ranges(self, start_date: str, weeks: int):
        date_format = "%m/%d/%Y"
        start = datetime.strptime(start_date, date_format)
        date_ranges = [(start.strftime(date_format), (start + timedelta(days=6)).strftime(date_format))]
        for _ in range(weeks - 1):
            start += timedelta(days=7)
            date_ranges.append((start.strftime(date_format), (start + timedelta(days=6)).strftime(date_format)))
        return date_ranges

    def login(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, proxy={
                "server": f"http://{self.proxy_host}:{self.proxy_port}",
                "username": self.proxy_user,
                "password": self.proxy_password
            })
            context = browser.new_context()
            stealth_sync(context)
            self.page = context.new_page()  # Store page in self.page
            self.page.goto(f"{self.base_url}/Logins/039/sites/betwar/index.aspx", timeout=60000)
            time.sleep(random.uniform(2, 5))
            self.page.fill("#txtAccessOfCode", self.username)
            self.page.fill("#txtAccessOfPassword", self.password)
            time.sleep(random.uniform(1, 3))
            self.page.click("input[type='submit']")
            print("Login successful.")
            time.sleep(random.uniform(2, 5))

            self.process_partners(self.page)  # Call processing function

    def scrape_total_volume(self, partner, page):
        """Scrapes only the Total Volume row for the partner."""
        try:
            total_volume_element = page.locator("//tr[@class='rowTotal']/td[6]/span")
            total_volume_element.wait_for(state="visible", timeout=5000)
            total_volume = total_volume_element.text_content().strip()
            print(f"{partner}: {total_volume}")
            return total_volume

        except Exception as e:
            print(f"⚠️ Error scraping total volume for {partner}: {e}")


    def scrape_performance_table(self, page, partner, date_range, total_volume):
        all_rows_data = []  
        try:
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            total_row = soup.find("tr", {"class": "rowTotal"})
            
            if total_row:
                cells = total_row.find_all("td")
                if len(cells) >= 6: 
                    total_volume = cells[5].text.strip()
                    
                    existing_entry = next(
                        (entry for entry in all_rows_data 
                        if entry["partnername"] == partner 
                        and entry["daterange"] == date_range),
                        None
                    )
                    
                    if not existing_entry:
                        all_rows_data.append({
                            "partnername": partner,
                            "daterange": date_range,
                            "totalvolume": total_volume
                        })
                        print(f"✅ Added unique entry for {partner} - {date_range}")
                    else:
                        print(f"⚠️ Duplicate skipped for {partner} - {date_range}")
                else:
                    print(f"⚠️ Not enough cells in total row for {partner}")
            else:
                print(f"⚠️ Total row not found for {partner}")

            print("📊 Final Clean Data:")
            for entry in all_rows_data:
                print(f"Partner: {entry['partnername']} | Date Range: {entry['daterange']} | Total: {entry['totalvolume']}")
                
        except Exception as e:
            print(f"⚠️ Error in processing {partner}: {str(e)}")

    def process_partners(self, page):
        for partner in self.partners_to_select:
            try:
                page.goto(f"{self.base_url}/Agent/Home.aspx", wait_until="networkidle")
                time.sleep(3)

                # Click the dropdown button
                dropdown_button = page.locator("xpath=/html/body/form/header/nav/div/div[2]/div/div/nav/div[1]/div[1]/div[2]/div/div/div/button")
                dropdown_button.wait_for(state="visible", timeout=5000)
                dropdown_button.click()
                time.sleep(2)

                # Click "Show Tree" button if visible
                show_tree_button = page.locator(".btn-showtree")
                if show_tree_button.is_visible():
                    show_tree_button.click()
                    time.sleep(3)

                # Get the dropdown select element
                select_element = page.locator(".cbo-agentList")
                select_element.wait_for(state="visible", timeout=5000)

                # Get all available options
                available_partners = select_element.locator("option").all_text_contents()
                available_partners = [opt.strip() for opt in available_partners if opt.strip()]

                # Check if the partner exists
                matching_option = next((opt for opt in available_partners if partner.lower() in opt.lower()), None)
                if matching_option:
                    select_element.select_option(label=matching_option)
                    print(f"✅ Successfully selected: {matching_option}")

                    # Wait for dropdown selection effect
                    page.wait_for_timeout(3000)

                    # Wait for the page to settle before moving
                    page.wait_for_load_state("networkidle")

                    # **Fix: Check if the page has changed before navigating**
                    if page.url != f"{self.base_url}/Agent/CustomerPerfomanceAgent.aspx":
                        page.goto(f"{self.base_url}/Agent/CustomerPerfomanceAgent.aspx", wait_until="domcontentloaded")
                        time.sleep(3)

                    # Set date range
                    date_from, date_to = self.date_ranges[0]
                    total_volume = self.scrape_total_volume(partner, page)

                    try:
                        from_date_input = page.locator("#ctl00_cphWorkArea_dtpDateFrom_dateInput")
                        from_date_input.wait_for(state="visible", timeout=5000)
                        from_date_input.fill(date_from)
                        from_date_input.press("Enter")
                        time.sleep(2)

                        to_date_input = page.locator("#ctl00_cphWorkArea_dtpDateTo_dateInput")
                        to_date_input.wait_for(state="visible", timeout=5000)
                        to_date_input.fill(date_to)
                        to_date_input.press("Enter")

                        print(f"📅 Selected date range: {date_from} to {date_to}")
                        time.sleep(5)

                        # Call scrape_total_volume (converted for Playwright)
                        self.scrape_total_volume(partner, page)
                        self.scrape_performance_table(page, partner, f"{date_from} to {date_to}", total_volume)

                    except Exception as e:
                        print(f"⚠️ Error setting date range: {e}")

                else:
                    print(f"❌ Partner {partner} not found in the dropdown.")

            except Exception as e:
                print(f"⚠️ Error processing partner {partner}: {e}")
        
        print("🎯 Process completed successfully.")
    def close(self):
        print("Closing resources")


if __name__ == "__main__":
    bot = PartnerVolume(
        username="spades",
        password="yoguy$",
        base_url="https://betwar.com"
    )
    proxy_list = bot.fetch_proxies()
    bot.get_random_proxy(proxy_list)
    bot.verify_proxy()
    bot.login()
    bot.close()