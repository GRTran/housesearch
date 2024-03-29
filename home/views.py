from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import SearchForm, URLForm
import random


class HomeView(TemplateView):
    """Extends the ``FormView`` to create a search form on the home view.
    """
    template_name = "home/landing_page.html"

    def get(self, request, *args, **kwargs):
        context = {
            "search_form": SearchForm(prefix="search_form_pre"),
            "url_form": URLForm(prefix="url_form_pre"),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        # Check which form has been selected
        hash = random.getrandbits(128)
        if "search_form_pre" in request.POST:
            # The detailed search form
            max_price = request.POST["search_form_pre-max_price"]
            min_price = request.POST["search_form_pre-min_price"]
            min_bedrooms = request.POST["search_form_pre-max_bedrooms"]
            max_bedrooms = request.POST["search_form_pre-max_bedrooms"]
            postcode = request.POST["search_form_pre-postcode"]
            radius = request.POST["search_form_pre-radius"]
            response = HttpResponseRedirect(reverse('scraper.listings',
            kwargs = {
                "max_price": max_price, "min_price": min_price, "postcode": postcode,
                "max_bedrooms": max_bedrooms, "min_bedrooms": min_bedrooms, "radius": radius,
                "flag": "detailed_search",
            }))
        elif "url_form_pre" in request.POST:
            # The url option has been selected with fixed url.
            response = HttpResponseRedirect(reverse('scraper.url.listings', 
                kwargs= {"key": request.POST["url_form_pre-urls"], "flag": "urls", "hashref": hash}
                ))
				
        
        return response