from typing import Any, Dict
from django.shortcuts import render
from django import forms
from django.views.generic import ListView, TemplateView, DetailView, UpdateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpRequest, JsonResponse
from django.urls import reverse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_protect
import pandas as pd

from scraper.models import Listing
from scraper.web_scrape import rightmove_listings as rightmove
from scraper.forms import LikedForm
import locale
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

class ListingsView(ListView):
	model = Listing
	context_object_name = 'listing'
	template_name = 'scraper/listings.html'
	paginate_by = 10
	listings: rightmove
	search_result: pd.DataFrame
	
	def get_queryset(self):
		'''
		Overriding the default queryset that returns a list of model objects that will be added to the context. Handles all overheads with adding a list to context using this approach. No need to override get_context_data and the get function
		'''
		# TODO: Make this into a pagination so that we don't need to load 500+ all at once. Will need to alter the search listings

		# Create the rightmove object and search based on criteria
		self.listings = rightmove()

		# Check the data to see whether the url or criteria has been provided
		if self.kwargs.get("flags") == "urls":
			url = self.kwargs.get("url")
			self.listings.attach_url(url)
			postcode = None
		else:
			# Criteria
			max_price = self.kwargs["max_price"]
			min_price = self.kwargs["min_price"]
			max_bedrooms = self.kwargs["max_bedrooms"]
			min_bedrooms = self.kwargs["min_bedrooms"]
			radius = self.kwargs["radius"]
			postcode = self.kwargs["postcode"]
			self.listings.attach_url(postcode, max_price, min_price, min_bedrooms, max_bedrooms, radius)
		# Get the dataframe of listings and data
		self.search_result = self.listings.get_listings()

		
		self.listings.listing_links(postcode)

		# Create a QuerySet (List) of Listing objects
		qs = []
		for _, item in self.search_result.iterrows():
			# Look for an existing listing in the current database, checking is previously liked.
			try:
				# Item found
				result = Listing.objects.get(item['id'])
			except:
				result = None
			
			qs += [Listing(id=item['id'], title=item['title'], price=item['price'], url=item['url'],
				image_url=item['image_url'], date_listed=item['date_listed'], reduced=item['reduced'],
				region_id=item['region_id'])]
			
			if result != None:
				# Setting the Liked paramter for the Listing queryset object.
				qs[-1].liked = result.liked
		
		return qs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = LikedForm # The POST request from the form will now be routed through the form class. This handles the case where the Listview does not have a POST function. GET is still handled through the listview and will call the get_queryset.
		return context
	

# Create an AJAX endpoint that will process the like/dislike and add to listings database of liked properties
@csrf_protect
def set_like(request):
	print('FOUND ENDPOINT')
	# fields = Listing._meta.get_fields()
	# for field in fields:
	# 	print(field.attname)
	print(request.POST.get("id"))
	print(request.POST.get("like_dislike"))

	id = int(request.POST.get("id"))
	status = request.POST.get("like_dislike")
	_edit_item(id, status)
	return JsonResponse({'' : '<a class="likebutton" id="like" data-catid="AAA" href="#">disLike</a>'})

def _edit_item(id, data):
	try:
		# item exists so update the DB.
		item = Listing.objects.get(pk=id)
		item.liked = option
	except:
		# Item does not exist so add it to DB.
		item = Listing(
						id=item['id'], title=item['title'], price=item['price'], 
						url=item['url'], image_url=item['image_url'], date_listed=item['date_listed'],
						reduced=item['reduced'], region_id=item['region_id']
					)

	item.save()


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

		tmp_url = item.url.split(sep='?')[0]+'media?'+item.url.split(sep='?')[1]
		outs, image_urls = indi_listing.listing_detail(item.url)

		ctx["image_urls"] = image_urls
		ctx["detailed_info"] = outs
		return self.render_to_response(ctx)
	
	def post(self, request, *args, **kwargs):
		return ListingLiked.post(request, *args, **kwargs)
	
class ListingLiked(FormView):
	# template_name = 'scraper/listings.html'
	form_class = LikedForm
	model = Listing

	def post(self, request, *args, **kwargs):
		print('here')
		ctx = super().get_context_data(**kwargs)
		print(ctx['info'])
		return ListingsView.get()
	
	
	
	def get_success_url(self):
		return reverse('scraper/listings.html')
	