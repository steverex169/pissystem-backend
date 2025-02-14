from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


class WeeklyFigureScraper:
    def __init__(self, email, password, base_url):
        self.email = email
        self.password = password
        self.base_url = base_url
        self.driver = None
        self.scraped_data = []

    def setup_driver(self):
        """Sets up the Selenium WebDriver."""
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()

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
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "calendar-prev"))
        )

        print("Selecting previous week...")
        prev_button = self.driver.find_element(By.ID, "calendar-prev")
        prev_button.click()
        time.sleep(3)
        print("Previous week selected.")

    def navigate_to_weekly_figure(self):
        """Navigates to the Weekly Figure page and selects the previous week."""
        print("Navigating to Weekly Figure page...")
        self.driver.get(f"{self.base_url}/reports/weekly-figure/0/0/0/0/0/0/-1/-1/0/0")

        # Wait for the "calendar-today" button to be present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "calendar-today"))
        )

        # Locate the button and print its text
        today_button = self.driver.find_element(By.ID, "calendar-today")
        today_text = today_button.text
        print(f"Today's date range: {today_text}")

        # Wait for the "calendar-prev" button to be present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "calendar-prev"))
        )

        print("Selecting previous week...")
        prev_button = self.driver.find_element(By.ID, "calendar-prev")
        prev_button.click()
        time.sleep(3)
        print("Previous week selected.")

    def process_dropdowns(self):
        """Processes all dropdowns on the Weekly Figure page."""
        total_dropdowns = len(self.driver.find_elements(By.CSS_SELECTOR, "td fa-icon.ng-fa-icon"))
        print(f"Total dropdowns found: {total_dropdowns}")

        for idx in range(total_dropdowns):
            try:
                print(f"Processing dropdown {idx + 1} of {total_dropdowns}...")
                partner_data = self.process_dropdown(idx + 1)
                if partner_data:
                    self.scraped_data.append(partner_data)
            except Exception:
                continue

        print("Scraping complete.")

    def process_dropdown(self, dropdown_index):
        """Processes a single dropdown and extracts its data."""
        # Locate parent row to get the partner name and summary data
        parent_row = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"(//td/fa-icon)[{dropdown_index}]/ancestor::tr"))
        )
        parent_cols = parent_row.find_elements(By.TAG_NAME, "td")
        partner_name = parent_cols[1].text.strip()  # Partner name
        total = parent_cols[2].text.strip()  # Total
        partner_profit = parent_cols[3].text.strip()  # Partner profit
        office_profit = parent_cols[4].text.strip()  # Office profit

        print(f"Partner: {partner_name}, Total: {total}, Partner Profit: {partner_profit}, Office Profit: {office_profit}")

        partner_data = {
            "partner_name": partner_name,
            "total": total,
            "partner_profit": partner_profit,
            "office_profit": office_profit,
            "dropdown_data": []
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
        for row in rows[1:]:  # Skip the header row
            cols = row.find_elements(By.TAG_NAME, "td")
            row_data = {
                "website_url": cols[0].text.strip(),
                "username": cols[1].text.strip(),
                "password": cols[2].text.strip(),
                "figure": cols[3].text.strip(),
                "affiliate_profit": cols[4].text.strip(),
                "office_profit": cols[5].text.strip()
            }
            print(f"    Website: {row_data['website_url']}, Username: {row_data['username']}, Password: {row_data['password']}, "
                  f"Figure: {row_data['figure']}, Affiliate Profit: {row_data['affiliate_profit']}, Office Profit: {row_data['office_profit']}")
            partner_data["dropdown_data"].append(row_data)

        # Collapse the dropdown after processing
        dropdown.click()
        time.sleep(2)  # Allow DOM to stabilize before moving to the next dropdown

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

    # Example: Use the scraped data
    print("\nFinal Scraped Data:")
    for partner in scraper.scraped_data:
        print(f"Partner Name: {partner['partner_name']}, Total: {partner['total']}, Partner Profit: {partner['partner_profit']}, Office Profit: {partner['office_profit']}")
        for entry in partner["dropdown_data"]:
            print(f"    Website: {entry['website_url']}, Username: {entry['username']}, Password: {entry['password']}, "
                  f"Figure: {entry['figure']}, Affiliate Profit: {entry['affiliate_profit']}, Office Profit: {entry['office_profit']}")
