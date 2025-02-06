from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from rest_framework import parsers
from rest_framework.permissions import IsAuthenticated, AllowAny
from .utils import WeeklyFigureScraper
from .utilsbetwar import WeeklyFigureScraperBetwar
from .volumnScrape import PartnerVolume
from .serializers import PartnerDataSerializer
from organizationdata.models import Scrapdata, ScrapBetwarVolumn
import logging
from rest_framework.views import APIView
from account.models import UserAccount
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
import logging


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

        # Process scraped data and save it to DB
        for partner in scraper.scraped_data:
            for entry in partner.get("dropdown_data", []):
                Scrapdata.objects.create(
                    partner_name=partner['partner_name'],
                    user=partner['partner_name'],
                    total=partner['total'],
                    partner_profit=partner['partner_profit'],
                    office_profit=entry.get('office_profit', None),
                    website_url=entry.get('website_url', None),
                    username=entry.get('username', partner['partner_name']),
                    password=entry.get('password', entry.get('username', '')),
                    figure=entry.get('figure', 0),
                    affiliate_profit=entry.get('affiliate_profit', 0),
                    office_profit_dropdown=entry.get('office_profit', None)
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
                    print("previous date with end date:", formatted_date_range, start_date, end_date)
                else:
                    formatted_date_range = "N/A"
            except Exception as e:
                logging.error(f"Date formatting error: {str(e)}")
                formatted_date_range = "N/A"

            # Log the check for existing data
        
            print(f"Creating new entry for {entry.get('name')}")
            Scrapdata.objects.create(
                partner="BETWAR",  # Default value
                partner_name=entry.get('partner_id') if entry.get('partner_id') else entry.get('user_id', "user_id"),
                user=entry.get('user_id', "N/A"),  # Match scraped data key
                total=entry.get('carry', "N/A"),  # Map 'carry' to 'total'
                partner_profit=formatted_date_range,  # Map 'payments' to 'partner_profit'
                office_profit=entry.get('balance', "N/A"),  # Map 'balance' to 'office_profit'
                username=entry.get('partner_id') if entry.get('partner_id') else entry.get('user_id', "user_id"),  # Match scraped data key
                password=entry.get('password') if entry.get('password') else entry.get('user_id', "user_id"),  # Match scraped data key
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

class VolumnScrapeBewar(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        base_url = request.data.get("base_url", "https://betwar.com")

        if not username or not password:
            return Response(
                {"error": "username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        scraper = PartnerVolume(username=username, password=password, base_url=base_url)

        try:
            proxy_list = scraper.fetch_proxies()
            scraper.get_random_proxy(proxy_list)
            scraper.verify_proxy()
            scraper.login()
        except Exception as e:
            logging.error(f"Scraper error: {str(e)}")
            return Response({"error": "Error during scraping."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            scraper.close()

        if not scraper.all_rows_data:
            return Response({"message": "No data found."}, status=status.HTTP_204_NO_CONTENT)

        created_entries = []  # To collect all created entries for response
        for entry in scraper.all_rows_data:
            if not isinstance(entry, dict):
                continue
            try:
                previous_date = entry.get('daterange')
                pname = entry.get('partnername')
                volumedata = entry.get('totalvolume')

                if previous_date:
                    date_parts = previous_date.split(" to ")
                    if len(date_parts) == 2:
                        start_date = datetime.strptime(date_parts[0], "%m/%d/%Y")
                        end_date = datetime.strptime(date_parts[1], "%m/%d/%Y")
                        formatted_date_range = f"{start_date.strftime('%-m/%-d/%y')} - {end_date.strftime('%-m/%-d/%y')}"
                    else:
                        formatted_date_range = "N/A"
                else:
                    formatted_date_range = "N/A"

                logging.info(f"Processing entry: partner={pname}, date={formatted_date_range}, volume={volumedata}")

                created_entries.append(ScrapBetwarVolumn.objects.create(
                    partner_name=pname,
                    weak_date=formatted_date_range,
                    volume=volumedata
                ))

            except Exception as e:
                logging.error(f"Error processing entry: {str(e)}")
                continue  # Continue to next entry in case of error

        if created_entries:
            return Response(
                {"message": "Scraping successful.", "data": [entry.id for entry in created_entries]},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "No new data saved."},
                status=status.HTTP_204_NO_CONTENT
            )






    