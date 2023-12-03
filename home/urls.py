from django.urls import path
from . import views

urlpatterns = [
	path('home', views.HomeView.as_view()),
	path('home/refresh_database', views.refresh_database)
    # path('home',views.HomeView.scrape(), name='scrape'),
	# path('home', views.home),
]
