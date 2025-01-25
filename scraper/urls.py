from django.urls import path
from .views import ScrapeWeeklyFiguresView, WeeklyFigureScraperAPI

urlpatterns = [
    path('scrape-weekly-figures/', ScrapeWeeklyFiguresView.as_view(), name='scrape-weekly-figures'),
    path('scrape-weekly-figures-betwar/', WeeklyFigureScraperAPI.as_view(), name='scrape-weekly-figures-betwar'),

]

