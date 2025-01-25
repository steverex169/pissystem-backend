from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from rest_framework import parsers
from rest_framework.permissions import IsAuthenticated, AllowAny
from .utils import WeeklyFigureScraper
from .utilsbetwar import WeeklyFigureScraperBetwar
from .serializers import PartnerDataSerializer
from organizationdata.models import Scrapdata
import logging
from rest_framework.views import APIView
from account.models import UserAccount
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta



# class ScrapeWeeklyFiguresView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")
#         base_url = request.data.get("base_url")

#         if not email or not password or not base_url:
#             return Response(
#                 {"error": "email, password, and base_url are required."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         scraper = WeeklyFigureScraper(email, password, base_url)
#         try:
#             scraper.setup_driver()
#             scraper.login()
#             scraper.navigate_to_weekly_figure()
#             scraper.process_dropdowns()
#         except Exception as e:
#             logging.error(f"Scraper error: {str(e)}")
#             return Response({"error": "Error during scraping."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         finally:
#             scraper.close()

#         if not scraper.scraped_data:
#             return Response({"error": "No data scraped."}, status=status.HTTP_204_NO_CONTENT)

#         # Process scraped data
#         for partner in scraper.scraped_data:
#             for entry in partner["dropdown_data"]:
#                 if not Scrapdata.objects.filter(
#                     website_url=entry['website_url'], username=entry['username']
#                 ).exists():
#                     # Save new entry
#                     Scrapdata.objects.create(
#                         partner_name=partner['partner_name'],
#                         total=partner['total'],
#                         partner_profit=partner['today_text'],
#                         office_profit=partner['office_profit'],
#                         website_url=entry['website_url'],
#                         username=entry['username'],
#                         password=entry['password'],
#                         figure=entry['figure'],
#                         affiliate_profit=entry['affiliate_profit'],
#                         office_profit_dropdown=entry['office_profit']
#                     )
#         # Serialize and return response
#         serialized_data = PartnerDataSerializer(scraper.scraped_data, many=True).data
#         return Response(
#             {"message": "Data scraped successfully.", "data": serialized_data},
#             status=status.HTTP_200_OK
        # )
    
from datetime import datetime

class ScrapeWeeklyFiguresView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        base_url = request.data.get("base_url")

        if not email or not password or not base_url:
            return Response(
                {"error": "email, password, and base_url are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        scraper = WeeklyFigureScraper(email, password, base_url)
        try:
            scraper.setup_driver()
            scraper.login()
            scraper.navigate_to_weekly_figure()
            scraper.process_dropdowns()
        except Exception as e:
            logging.error(f"Scraper error: {str(e)}")
            return Response({"error": "Error during scraping."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            scraper.close()

        if not scraper.scraped_data:
            return Response({"error": "No data scraped."}, status=status.HTTP_204_NO_CONTENT)

        # Process scraped data
        for partner in scraper.scraped_data:
            # Extract the date range from partner['today_text']
            date_range = partner['today_text']
            try:
                start_date_str, end_date_str = date_range.split(" - ")
                start_date = datetime.strptime(start_date_str, "%m/%d/%y")
                end_date = datetime.strptime(end_date_str, "%m/%d/%y")

                # Format dates to "12 Jan 2024" format
                formatted_start_date = start_date.strftime("%d %b %Y")
                formatted_end_date = end_date.strftime("%d %b %Y")

                print("Start Date:", formatted_start_date)
                print("End Date:", formatted_end_date)
            except ValueError as e:
                print(f"Error parsing date range '{date_range}': {str(e)}")
                continue

            for entry in partner["dropdown_data"]:
                if not Scrapdata.objects.filter(
                    website_url=entry['website_url'], username=entry['username']
                ).exists():
                    # Save new entry
                    Scrapdata.objects.create(
                        partner_name=partner['partner_name'],
                        total=partner['total'],
                        partner_profit=partner['today_text'],
                        office_profit=entry['office_profit'],
                        website_url=entry['website_url'],
                        username=entry['username'],
                        password=entry['password'],
                        figure=entry['figure'],
                        affiliate_profit=entry['affiliate_profit'],
                        office_profit_dropdown=entry['office_profit']
                    )
        # Serialize and return response
        serialized_data = PartnerDataSerializer(scraper.scraped_data, many=True).data
        return Response(
            {"message": "Data scraped successfully.", "data": serialized_data},
            status=status.HTTP_200_OK
        )



class WeeklyFigureScraperAPI(APIView):
    """
    API endpoint to scrape weekly figures from Betwar.
    """

    def post(self, request):
        # Extract input data from the POST request
        username = request.data.get("username")
        password = request.data.get("password")
        base_url = request.data.get("base_url", "https://betwar.com")  # Use default if not provided

        # Validate input data
        if not username or not password:
            return Response(
                {"error": "username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize the scraper
        try:
            scraper = WeeklyFigureScraperBetwar(username=username, password=password, base_url=base_url)

            # Verify proxy and scrape data
            scraper.verify_proxy()
            scraped_data = scraper.scrape_data()
        except Exception as e:
            logging.error(f"Scraper error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check if data was scraped
        if not scraped_data:
            return Response({"message": "No data found."}, status=status.HTTP_204_NO_CONTENT)
        for entry in scraped_data:
            print("Entry:", entry)  # Debugging: Inspect the entry
            if not isinstance(entry, dict):
                continue
            try:
                previous_date = entry.get('previous_week_date')
                if previous_date:
                    # Parse the date from the scraped data
                    start_date = datetime.strptime(previous_date, "%m/%d/%Y")  # Adjust format if necessary
                    end_date = start_date + timedelta(days=6)  # Add 6 days for the 7-day range
                    formatted_date_range = f"{start_date.strftime('%m/%d/%y')} - {end_date.strftime('%m/%d/%y')}"
                    print("previous ate with end date", formatted_date_range, start_date, end_date)
                else:
                    formatted_date_range = "N/A"
            except Exception as e:
                logging.error(f"Date formatting error: {str(e)}")
                formatted_date_range = "N/A"
            if not Scrapdata.objects.filter(username=entry.get('name')).exists():
                Scrapdata.objects.create(
                    partner="BETWAR",  # Default value
                    partner_name=entry.get('user_id', "N/A"),  # Match scraped data key
                    total=entry.get('carry', "N/A"),  # Map 'carry' to 'total'
                    partner_profit=formatted_date_range,  # Map 'payments' to 'partner_profit'
                    office_profit=entry.get('balance', "N/A"),  # Map 'balance' to 'office_profit'
                    username=entry.get('name', "N/A"),  # Assuming 'name' is the username
                    password=entry.get('password', "N/A"),  # Match scraped data key
                    figure="N/A",  # Default value if not scraped
                    affiliate_profit=entry.get('payments', "N/A"),  # Default value if not scraped
                    weekly=entry.get('weekly', "N/A"),  # Default value if not scraped
                    office_profit_dropdown="N/A",  # Default value if not scraped
                    website_url="N/A",  # Hardcoded URL
                )
        # Return the scraped data
        return Response(
            {"message": "Scraping successful.", "data": scraped_data},
            status=status.HTTP_200_OK
        )
