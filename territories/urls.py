from django.urls import path

from territories.views import  TerritoriesDitrictCityListView, TerritoriesListView


urlpatterns = [
    path('territories-list/',
         TerritoriesListView.as_view(), name='territories-list'),
    path('district-city-list/',
         TerritoriesDitrictCityListView.as_view(), name='district-city-list'),

]
