from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from datetime import datetime

from .models import Listing

class HomeView(TemplateView):
    template_name = "home/landing_page.html"

    # Obtain QuerySet from the model object, no manipulation required here, simply pass it through to the template for representing information
    listings = Listing.objects.all()
    extra_context = {'today': datetime.today(), "listings": listings}

    # We are going to create trading card like shapes to present the house data that is present in the database

    # Lets start off by having a button called scrape that when activated, performs the scraping
    def scrape():
        print('scrape test')
        pass

# Have a button that runs the scrape from the home view
# class CreateHomeView(CreateView):
#     pass

