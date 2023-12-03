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
		
		# Check the data to see whether the url or criteria has been provided
		if self.kwargs.get("flag") == "urls" and not self.listings.attached:
			# URL not set so this must be the first call
			url = url_refs.get(self.kwargs.get("key"))
			hash = self.kwargs.get("hashref")
			self.listings.attach_ref_url(url)
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

		# Reset the searched listings if hashref doesn't match current search hash
		if len(SearchedListings.objects.filter(hashref = hash)) == 0:
			SearchedListings.objects.all().delete()
		# Create temporary queryset object
		if self.qs is None:
			self.qs = [None for _ in range(self.listings.nlistings -1)]

		# Try and get the page number required from the request
		if self.request.GET.get("page") is not None:
			page_num = int(self.request.GET.get("page"))
		else:
			page_num = 1

		# Getting first and last cntry in the vector of all entries
		start, end = (page_num-1)*self.listings.nperpage, page_num*self.listings.nperpage

		# Check already scraped data for listings from a page
		# Check that the hash key in the searched_listings is the same, then same search session.
		search_listings = SearchedListings.objects.filter(page=page_num)

		if len(search_listings) == 0:
			# Get the listings
			self.listings.listing_links(page_num)
			# Perform the search and populate the qs
			self._qs_from_search(page_num, hash, start, end)
		else:
			# Return the page that has previously been searched
			self.qs[start:end] = [Listing.objects.get(id=key.id) for key in search_listings]

		return self.qs

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
	print('FOUND ENDPOINT')
	# fields = Listing._meta.get_fields()
	# for field in fields:
	# 	print(field.attname)
	print(request.POST.get("id"))
	print(request.POST.get("like_dislike"))

	id = int(request.POST.get("id"))
	if request.POST.get("like_dislike") == "Like":
		status = 2
	elif request.POST.get("like_dislike") == "Dislike":
		status = 1
	else:
		status = 0
	_edit_item(id, status)
	return JsonResponse({'result' : 'success'})

def _edit_item(id, status):
	try:
		# item exists so update the DB.
		item = Listing.objects.get(pk=id)
		item.liked = status
	except:
		# Item does not exist so add it to DB.
		item = Listing(
						id=item['id'], title=item['title'], price=item['price'], 
						url=item['url'], image_url=item['image_url'], date_listed=item['date_listed'],
						reduced=item['reduced'], region_id=item['region_id'], 
					)
	
	# Get the detailed listing information

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
	