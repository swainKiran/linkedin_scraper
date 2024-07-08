# scraper/urls.py
from django.urls import path
from .views import scrape_data, view_data

urlpatterns = [
    path('scrape/', scrape_data, name='scrape_data'),
    path('data/', view_data, name='view_data'),
]
