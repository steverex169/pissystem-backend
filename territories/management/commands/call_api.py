from datetime import datetime
from django.core.management.base import BaseCommand
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
import pytz

from auditoradmin.views import PendingAuditsView

class Command(BaseCommand):
    help = 'Calls the API'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__('call_api', *args, **kwargs)

    def handle(self, *args, **options):
        # Create an instance of your API view
        view = PendingAuditsView.as_view()

        # Create a DRF test client
        client = APIClient()

        # Set the time zone to UTC
        tz = pytz.timezone('UTC')
        now = timezone.now().astimezone(tz)

        # Call the API
        url = reverse('pending-audits')
        response = client.get(url, {'date': now.date()}, format='json')
        if response.status_code == 200:
            print(self.style.SUCCESS('Successfully called API'))
        else:
            print(self.style.ERROR(f'Failed to call API. Status code: {response.status_code}'))
