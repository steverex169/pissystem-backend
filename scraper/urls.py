from django.urls import path
from .views import ScrapeWeeklyFiguresView, WeeklyFigureScraperAPI, VolumnScrapeBewar

urlpatterns = [
    path('scrape-weekly-figures/', ScrapeWeeklyFiguresView.as_view(), name='scrape-weekly-figures'),
    path('scrape-weekly-figures-betwar/', WeeklyFigureScraperAPI.as_view(), name='scrape-weekly-figures-betwar'),
    path('scrape-volume-betwar/', VolumnScrapeBewar.as_view(), name='scrape-volume-betwar'),

]

