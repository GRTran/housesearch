from django.urls import path
from . import views

urlpatterns = [
	path('home', views.HomeView.as_view()),
	path('home/update_search', views.update_search),
  path('home/add_url', views.add_url)
]
