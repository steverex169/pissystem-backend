
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
