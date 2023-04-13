from django.urls import path
from . import views

urlpatterns = [
	path('home', views.HomeView.as_view()),
    path('home',views.HomeView.scrape(), name='scrape'),
	# path('home', views.home),
]
