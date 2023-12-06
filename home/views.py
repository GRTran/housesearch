from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import SearchForm, URLForm
import random
from scraper.models import Listing
from bs4 import BeautifulSoup as bs
import requests
import re
import logging
import random
from datetime import datetime, timedelta

url_refs = {"South West": 'https://www.rightmove.co.uk/property-for-sale/find.html?minBedrooms=3&propertyTypes=detached%2Csemi-detached%2Cterraced%2Cbungalow&keywords=&sortType=6&viewType=LIST&channel=BUY&maxPrice=550000&radius=0.0&locationIdentifier=USERDEFINEDAREA^{"polylines"%3A"eq|xHpbeAl`%40q~Gz_AgzGey%40geDkRsiDbq%40i|AtiDt|Czm%40p_B|_AkmG`Iwv%40vOcm%40l{AuHjmAbObnEzi%40dnAxeAwEjuDtAjwClLhqE`oEdfCngAi_L|uEllBlzAvwEeSn}Mwt%40dvToPn_MyQb}KubCxlD{pGwnCqeEzKadErt%40_mCzZqsBgoQsfGwfc%40"}&index='}


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
    
def refresh_database(request):
    """Take in a POST request from a button action and refresh the Listings database.
        1) We get the listings database and get the most recent listing. 
        2) We query rightmove according to newest to oldest. 
        3) We then see record additional properties that are newer than current date.
        4) We need to check to see if a company goes to reduced from new listing so that
        we dont double count it.
    """
    # 1) Get the existing entries in the database
    db = Listing.objects.all().order_by("date_listed")
    
    # Sort the database into when they were added to the site.
    try:
        newest = db[-1].date_listed
    except:
        # The database must be empty
        newest = None
    update_database(url_refs["South West"], newest)
    
    # Search rightmove listings by newest
    response = HttpResponseRedirect(reverse('scraper.url.listings', 
                kwargs= {"key": request.POST["url_form_pre-urls"], "flag": "urls", "hashref": hash}
                ))
    
def update_database(url, date_in_db):
    '''
    Searches a particular index of listings depending on the result of the pagination.
    '''
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    # Get the url page
    page = 0
    count = 0
    nresults = 1
    while count < nresults:
        # Get the single page response
        response = requests.get(url+str(page), headers=headers)
        # Parse through bs4
        soup = bs(response.content, 'html.parser')

        # # number of total listings
        if page == 0:
            nresults = int(soup.find('span', {'class' : 'searchHeader-resultCount'}).string)
            
        # Get the number of properties on the page
        properties = soup.findAll('div', {'class' : 'l-searchResult'})
        
        for prop in properties:
            # Check the date
            date_info = prop.find("span", {"class":"propertyCard-branchSummary-addedOrReduced"}).string
            # Split by regex
            add_reduce, date = split(date_info)
            if isinstance(date_in_db, datetime) and date < date_in_db:
                # Most recent searched so return because update of DB is complete
                return
            
            # Try and download the image of the property to the db
            id = int(link.split('/')[2][:-1])
            image_url = prop.img['src']
            img_name = download_image(image_url, id, 1)
            
            # Extract data from the property and add it to database
            link = prop.find('a', {'class' : 'propertyCard-link'})['href']
            info = {
                "id": id,
                "title": prop.address.span.string,
                "description": prop.find("span", {"data-test": "property-description"}).text,
                "price": int(''.join(re.findall(r'\d+', prop.find('div', {'class' : 'propertyCard-priceValue'}).string))),
                "url": 'https://rightmove.co.uk' + link,
                "image_url": img_name,
                "num_images": int(prop.find('span', {'class' : 'propertyCard-moreInfoNumber'}).string.split('/')[0]),
                "reduced": add_reduce,
                "date_listed": date,
            }
            
            check_update_listing(info)
            
            count += 1
        page += 1
    return

def split(date_info: str) -> tuple:
    """Reads in a string with date added info and whether it is new listing or reduced

    Args:
        date_info (str): _description_

    Returns:
        tuple: _description_
    """
    # Regex options
    add_type = {"reduced": True, "added": False}
    recent_add = {"today", "yesterday"}
    # Declare outputs
    found1 = None
    found2 = None
    # Make all lower case
    date_info = date_info.lower()
    # Form regex for type and search
    for tmp in add_type.keys():
        if re.search(tmp, date_info) is not None:
            found1 = add_type[tmp]
    # Form regex for date and search
    match = re.search("today", date_info)
    if match is not None:
        found2 = datetime.now()
        return found1, found2
    
    match = re.search("yesterday", date_info)
    if match is not None:
        found2 = datetime.now() - timedelta(1)
        return found1, found2
    
    match = re.search(r'(\d+/\d+/\d+)', date_info)
    if match is not None:
        found2 = datetime.strptime(match(1), "%d/%m/%Y")
        return found1, found2
        
    
def check_update_listing(entries: dict):
    obj = Listing.objects.filter(id)
    if obj is not None:
        # Delete old version of listing and add the new one
        obj.delete()
    # Add the new listing
    ent = Listing(**entries)
    ent.save()

def download_image(url, id, img_num) -> bool:
    """Downloads an image into the filesystem and returns bool for success/failure"""
    hash = random.getrandbits(128)
    try:
        data = requests.get(url).content
        with open(f"static/images/houses/{id}_{img_num}.jpg", "wb") as img:
            img.write(data)
            return f"{id}_{img_num}.jpg"
    except Exception:
        logging.WARNING(f"Cannot download image at url: {url}, skipping!")
        return None
    
    