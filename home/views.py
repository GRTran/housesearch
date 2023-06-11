from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime

# Import model from other folder that performs the search on a post request to the TemplateView.
# Then render the other get view to the response
from scraper.models import Listing
from scraper.web_scrape import rightmove_listings as rightmove

class HomeView(TemplateView):
    template_name = "home/landing_page.html"

    # Obtain QuerySet from the model object, no manipulation required here, simply pass it through to the template for representing information
    # listings = Listing.objects.all()
    # extra_context = {'today': datetime.today(), "listings": listings}

    # We are going to create trading card like shapes to present the house data that is present in the database

    #
    def post(self, request, *args, **kwargs):
        # Criteria
        max_price = 600000
        min_price = 0
        min_bedrooms = ''
        region_id = '5E1296'
        max_bedrooms = '2'
        radius = '0.5'

        # Get the listings from rightmove
        listings = rightmove()
        listings.search_listings(region_id, max_price, min_price, min_bedrooms, max_bedrooms, radius)
        df = listings.get_listings()

        # Populate the model with listings, making sure to not add duplicates of listings
        for index, item in df.iterrows():			
            try:
                result = Listing.objects.get(item['id'])
            except:
                result = None
        	# add or edit the listing if it is required
            if result == None:
        	    # the listing hasn't been recorded on the database, so add it
                l = Listing(id=item['id'], title=item['title'], price=item['price'], url=item['url'], image_url=item['image_url'], date_listed=item['date_listed'], reduced=item['reduced'], region_id=item['region_id'])
                l.save()
            elif result.price != item['price']:
        		# the listing exists but the price has been changed, so update the listing
                result.delete()
                l = Listing(id=item['id'], title=item['title'], price=item['price'], url=item['url'], image_url=item['image_url'], date_listed=item['date_listed'], reduced=item['reduced'], region_id=item['region_id'])
                l.save()
				
        # return HttpResponseRedirect(reverse('scraper.listings', args=(max_price, min_price, min_bedrooms, region_id, max_bedrooms, radius,)))
        response = HttpResponseRedirect(reverse('scraper.listings',
            kwargs = {
                "max_price": max_price, "min_price": min_price, "region_id": region_id,
                "max_bedrooms": max_bedrooms, "min_bedrooms": min_bedrooms, "radius": radius
            }))
        return response
# Have a button that runs the scrape from the home \view
# class CreateHomeView(CreateView):
#     pass

