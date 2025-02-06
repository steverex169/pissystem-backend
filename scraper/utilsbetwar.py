from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import time
import random


class WeeklyFigureScraperBetwar:
    def __init__(self, username, password, base_url="https://betwar.com"):
        self.username = username
        self.password = password
        self.base_url = base_url

    def scrape_data(self):
        """Scrape data from the Betwar website without proxies and in headless mode."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Running in headless mode
            context = browser.new_context()
            stealth_sync(context)  # Apply stealth mode to avoid bot detection
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
                previous_week_date = options[1] if len(options) > 1 else "Not found"
                print("Previous Week Date:", previous_week_date)

                # Scrape the table data
                page.wait_for_selector("#tblfigure", timeout=15000)
                rows = page.query_selector_all("#tblfigure tr")
                print("Scraping table data...")
                scraped_data = []

                if rows:
                    current_partner_id = ""

                    for row in rows[1:]:
                        cells = row.query_selector_all("td")

                        if len(cells) > 0:
                            first_cell_text = cells[0].text_content().strip()

                            # Check if cells[1] and cells[14] are empty
                            if not cells[1].text_content().strip() and not cells[14].text_content().strip():
                                current_partner_id = first_cell_text
                                print(f"New Partner ID Detected: {current_partner_id}")
                                continue

                            row_data = {
                                "partner_id": current_partner_id,
                                "user_id": first_cell_text,
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
