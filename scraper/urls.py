from django.urls import path
from scraper import views

urlpatterns = [
    path('listings/<max_price>&<min_price>&<postcode>&<max_bedrooms>&<radius>&<min_bedrooms>&<flag>',
         views.ListingsView.as_view(), name='scraper.listings'),
    path('listings/<key>&<flag>&<hashref>', views.ListingsView.as_view(), name='scraper.url.listings'),
    path('listings/listing_container/<int:pk>', views.ListingContainer.as_view(), name='scraper.listing_container'),
    path('listings/set_like', views.set_like, name="set_like")
]
