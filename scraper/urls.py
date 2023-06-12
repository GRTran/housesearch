from django.urls import path
from scraper import views

urlpatterns = [
    path('listings/<max_price>&<min_price>&<region_id>&<max_bedrooms>&<radius>&<min_bedrooms>&',
         views.ListingsView.as_view(), name='scraper.listings'),
    path('like_dislike/', views.ListingLiked.as_view(), name='scraper.like_dislike'),
    path('listings/listing_container/<int:pk>', views.ListingContainer.as_view(), name='scraper.listing_container')
]
