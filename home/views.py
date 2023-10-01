from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import SearchForm, URLForm


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
        if "search_pre" in request.POST:
            # The detailed search form
            max_price = request.POST["max_price"]
            min_price = request.POST["min_price"]
            min_bedrooms = request.POST["max_bedrooms"]
            max_bedrooms = request.POST["max_bedrooms"]
            postcode = request.POST["postcode"]
            radius = request.POST["radius"]
            response = HttpResponseRedirect(reverse('scraper.listings',
            kwargs = {
                "max_price": max_price, "min_price": min_price, "postcode": postcode,
                "max_bedrooms": max_bedrooms, "min_bedrooms": min_bedrooms, "radius": radius,
                "flag": "detailed_search",
            }))
        elif "url_pre" in request.POST:
            # The url option has been selected with fixed url.
            response = HttpResponseRedirect(reverse('scraper.listings', 
                kwargs= {"url": request.POST["urls"], "flag": "urls"}
                ))
				
        
        return response