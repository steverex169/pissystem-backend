import requests
import random
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync


class WeeklyFigureScraperBetwar:
    def __init__(self, username, password, base_url="https://betwar.com"):
        # User credentials
        self.username = username
        self.password = password
        self.base_url = base_url

        # Webshare proxy settings
        self.webshare_proxy_url = "https://proxy.webshare.io/api/v2/proxy/list/download/iouqvorexpcubufvlewcywrxypybuwottjggjjth/-/any/username/direct/-/"
        self.proxy_list = self.fetch_proxy_list()
        self.proxy_host, self.proxy_port, self.proxy_user, self.proxy_password = self.get_random_proxy()
        self.proxy_url = f"http://{self.proxy_user}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}"

    def fetch_proxy_list(self):
        """Fetch the proxy list from Webshare."""
        response = requests.get(self.webshare_proxy_url)
        proxy_list = response.text.strip().split("\n")
        if not proxy_list:
            raise Exception("No proxies fetched from the provided Webshare link.")
        return proxy_list

    def get_random_proxy(self):
        """Select a random proxy from the proxy list."""
        proxy = random.choice(self.proxy_list)
        proxy_host, proxy_port = proxy.split(":")[:2]
        proxy_user = "dtnvyuji"
        proxy_password = "pm5um6w7spc4"
        return proxy_host, proxy_port, proxy_user, proxy_password

    def verify_proxy(self):
        """Verify if the selected proxy is functional."""
        proxies = {"http": self.proxy_url, "https": self.proxy_url}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://google.com",
            "Connection": "keep-alive",
        }
        try:
            response = requests.get("https://ipinfo.io/json", proxies=proxies, headers=headers, timeout=10)
            response.raise_for_status()
            ip_data = response.json()
            print("Proxy verification result:")
            print(f"Public IP: {ip_data.get('ip')}")
            print(f"Location: {ip_data.get('city')}, {ip_data.get('region')}, {ip_data.get('country')}")
        except requests.exceptions.RequestException as e:
            print("Proxy verification failed.")
            raise Exception("Exiting script due to proxy verification failure.") from e

    def scrape_data(self):
        """Scrape data from the Betwar website."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, proxy={
                "server": f"http://{self.proxy_host}:{self.proxy_port}",
                "username": self.proxy_user,
                "password": self.proxy_password
            })
            context = browser.new_context()
            stealth_sync(context)  # Apply stealth mode to bypass bot detection
            page = context.new_page()

            try:
                # Navigate to the login page
                page.goto(f"{self.base_url}/Logins/039/sites/betwar/index.aspx", timeout=60000)
                time.sleep(random.uniform(2, 5))  # Simulate human-like delay

                # Fill in the username and password fields
                page.fill("#txtAccessOfCode", self.username)
                page.fill("#txtAccessOfPassword", self.password)
                time.sleep(random.uniform(1, 3))

                # Click the submit button
                page.click("input[type='submit']")
                print("Login successful.")
                time.sleep(random.uniform(2, 5))

                # Navigate to the 'Daily Figures' page
                page.goto(f"{self.base_url}/Agent/DailyFigures.aspx", timeout=60000)
                print("Navigated to the Daily Figures page.")

                # Wait for the 'Last Week' button to appear and click it
                page.wait_for_selector("#btnWeek2", timeout=15000)
                page.click("#btnWeek2")
                print("Clicked the 'Last Week' button.")
                time.sleep(random.uniform(2, 5))

                # Extract previous week date
                page.wait_for_selector(
                    "xpath=/html/body/form/main/div/div/div[2]/section/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/select"
                )
                element_text = page.locator(
                    "xpath=/html/body/form/main/div/div/div[2]/section/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/select"
                ).text_content()
                options = [line.strip() for line in element_text.split("\n") if line.strip()]
                if len(options) > 1:
                    previous_week_date = options[1]
                    print("Previous Week Date:", previous_week_date)
                else:
                    print("Previous week date not found.")

                # Scrape the table data
                page.wait_for_selector("#tblfigure", timeout=15000)
                rows = page.query_selector_all("#tblfigure tr")
                print("Scraping table data...")
                scraped_data = []  # Store extracted data here

                if rows:
                    for row in rows[1:]:  # Skip the header row
                        cells = row.query_selector_all("td")
                        row_data = {
                            "user_id": cells[0].text_content().strip() if len(cells) > 0 else "",
                            "name": cells[1].text_content().strip() if len(cells) > 1 else "",
                            "password": cells[14].text_content().strip() if len(cells) > 14 else "",
                            "carry": cells[3].text_content().strip() if len(cells) > 3 else "",
                            "payments": cells[12].text_content().strip() if len(cells) > 12 else "",
                            "balance": cells[13].text_content().strip() if len(cells) > 13 else "",
                            "previous_week_date": previous_week_date,
                            "weekly": cells[10].text_content().strip() if len(cells) > 10 else "",


                        }
                        scraped_data.append(row_data)
                else:
                    print("No rows found, skipping.")

                return scraped_data

            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                browser.close()
                print("Browser closed.")


