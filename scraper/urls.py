from django.urls import path
from scraper import views

urlpatterns = [
    path('listings/',views.ListingsView.as_view(), name='scraper.listings'),
    path('listings/listing_container/<int:pk>', views.ListingContainer.as_view(), name='scraper.listing_container')
]
