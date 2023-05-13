from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView, UpdateView
from django.http import HttpResponseNotFound

from scraper.models import Listing
from scraper.web_scrape import rightmove_listings as rightmove
import locale
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

class ListingsView(ListView):
	model = Listing
	context_object_name = 'listing'
	template_name = 'scraper/listings.html'
	
	def get_queryset(self):
		'''
		Overriding the default queryset that returns a list of model objects that will be added to the context. Handles all overheads with adding a list to context using this approach. No need to override get_context_data and the get function
		'''
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
			
		# Now render the list response based on the search criteria
		qs = Listing.objects.filter(price__lte = max_price) \
					   .filter(price__gte = min_price)
		return qs

class ListingContainer(TemplateView):
	'''
	Extend the template view, it is essentially a manual detail view but allows us to also send the contents in the context of the doc
	'''
	model = Listing
	context_object_name = 'list'
	template_name = 'scraper/listing_container.html'
	
	def get(self, request, *args, **kwargs):
		'''
		When getting the detailed view about the listing, we need to update the listing image urls
		'''
		ctx = super().get_context_data(**kwargs)


		try:
			item = self.model.objects.get(id=ctx['pk'])
			item.price = locale.currency(item.price, symbol=True, grouping=True, international=False)
			ctx["list"] = item
			# with the single listing, populate all of the information and present it in the html
		except self.model.DoesNotExist:
			ctx['list'] = None
			return HttpResponseNotFound()

		# Use the web-scrape module for individual webpages in order to get the information required to render them
		indi_listing = rightmove()

		# https://www.rightmove.co.uk/properties/133299740#/media?channel=RES_BUY
		# https://rightmove.co.uk/properties/133299740#/ media ?channel=RES_BUY

		tmp_url = item.url.split(sep='?')[0]+'media?'+item.url.split(sep='?')[1]
		outs, image_urls = indi_listing.listing_detail(item.url)

		ctx["image_urls"] = image_urls
		ctx["detailed_info"] = outs
		return self.render_to_response(ctx)
	
# class NotesUpdateView(UpdateView):
# 	model = Listing
# 	form_class = ListingForm
# 	success_url = '/smart/notes'