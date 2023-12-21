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
import json

from home.models import ReferenceURLs
from scraper.models import Listing, SearchedListings
from scraper.web_scrape import rightmove_listings as rightmove
from scraper.forms import LikedForm
import locale
locale.setlocale(locale.LC_ALL, 'en_US.utf8')

url_refs = {"South West": 'https://www.rightmove.co.uk/property-for-sale/find.html?minBedrooms=3&propertyTypes=detached%2Csemi-detached%2Cterraced%2Cbungalow&keywords=&sortType=2&viewType=LIST&channel=BUY&maxPrice=550000&radius=0.0&locationIdentifier=USERDEFINEDAREA^{"polylines"%3A"eq|xHpbeAl`%40q~Gz_AgzGey%40geDkRsiDbq%40i|AtiDt|Czm%40p_B|_AkmG`Iwv%40vOcm%40l{AuHjmAbObnEzi%40dnAxeAwEjuDtAjwClLhqE`oEdfCngAi_L|uEllBlzAvwEeSn}Mwt%40dvToPn_MyQb}KubCxlD{pGwnCqeEzKadErt%40_mCzZqsBgoQsfGwfc%40"}&index='}

class ListingsView(ListView):
	model = Listing
	context_object_name = 'listing'
	template_name = 'scraper/listings.html'
	paginate_by = 24
	# paginate_orphans = 4
	listings: rightmove
	search_result: pd.DataFrame
	
	def __init__(self):
		"""Initialise the rightmove object.
		"""
		super().__init__()
		self.listings = rightmove()
		self.qs = None

	def get_queryset(self):
		'''
		Overriding the default queryset that returns a list of model objects that will be added to the context. Handles all overheads with adding a list to context using this approach. No need to override get_context_data and the get function
		'''
		# Get the URLs model object from DB
		item = ReferenceURLs.objects.get(title=self.kwargs.get("ref"))
		# Use the reference to filter Listings database into queryset to display
		return Listing.objects.filter(referenceurls=item)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['form'] = LikedForm # The POST request from the form will now be routed through the form class. This handles the case where the Listview does not have a POST function. GET is still handled through the listview and will call the get_queryset.
		return context

	def _qs_from_search(self, page_num, hash, start, end):
		# Get the dataframe of listings and data
		self.search_result = self.listings.get_listings()

		count = 0
		for i in range(start, end):
			# Item from scrape
			item = self.search_result.iloc[count,:]
			try:
				# Item found in models, populate the queryset appropriately
				result = Listing.objects.get(id=item['id'])
				self.qs[i] = result
			except:
				# Create new listing object and save
				self.qs[i] = Listing(id=item['id'], title=item['title'], price=item['price'], url=item['url'],
					image_url=item['image_url'], date_listed=item['date_listed'], reduced=item['reduced'],
					region_id=item['region_id'], description=item["description"])
				# Add listing to db
				self.qs[i].save()
			count += 1

			try:
				searched = SearchedListings.objects.get(item['id'])
				# Item is found
			except:
				# Create an entry for searched listings to record already found pages
				searched = SearchedListings(id=item["id"], page=page_num, hashref = hash)
				searched.save()
			
	

# Create an AJAX endpoint that will process the like/dislike and add to listings database of liked properties
@csrf_protect
def set_like(request):
	# Get the like/dislike option from fetch request
	try:
		body = json.loads(request.body)
		option = body.get("option")
		id = int(body.get("id"))
		status_mapping = {"dislike": 1, "like": 2}
		status = status_mapping.get(option)
		if status is None:
			status = 0
		_edit_item(id, status)
		return JsonResponse({'result' : 'success'})
	except:
		return JsonResponse({'result' : 'failure'})

def _edit_item(id, status):
	try:
		# item exists so update the DB.
		item = Listing.objects.get(pk=id)
		item.liked = status
		item.save()
	except:
		pass

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
	