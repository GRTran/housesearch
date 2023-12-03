from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import SearchForm, URLForm
import random
from scraper.models import Listing
from bs4 import BeautifulSoup as bs
import requests
import re
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
    db = Listing.objects.all().order_by("date_listed", reverse=True)
    
    # Sort the database into when they were added to the site.
    newest = db[0]
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
    npage = 1
    while page < npage:
        # Get the single page response
        response = requests.get(url+str(page), headers=headers)
        # Parse through bs4
        soup = bs(response.content, 'html.parser')

        # # number of total listings
        if page == 0:
            npage = int(soup.find('span', {'class' : 'searchHeader-resultCount'}).string)
            
        # Get the number of properties on the page
        properties = len(soup.findAll('div', {'class' : 'l-searchResult'}))
        
        for prop in properties:
            # Check the date
            date_info = prop.find("span", {"class":"propertyCard-branchSummary-addedOrReduced"}).string
            # Split by regex
            add_reduce, date = split(date_info)
            if date < date_in_db:
                # Most recent searched
                return
            
            # Extract data from the property and add it to database
            link = prop.find('a', {'class' : 'propertyCard-link'})['href']
            url = 'https://rightmove.co.uk' + link
            id = int(link.split('/')[2][:-1])
            title = prop.address.span.string
            image_url = prop.img['src']
            price = int(''.join(re.findall(r'\d+', prop.find('div', {'class' : 'propertyCard-priceValue'}).string)))
            num_images = int(prop.find('span', {'class' : 'propertyCard-moreInfoNumber'}).string.split('/')[0])
            description = prop.find("span", {"data-test": "property-description"}).text
            
            # Check the listing db and if not present or change in any data then add it, else skip (should always be not present)
            
        
        page += 1
    
    # Count the number of cols and extract vector of dates. 

    # num_listings = 23
    # Using the page number calculate the correct starting number of property to show
    i = (24) * (nlistings)

    response = requests.get(self.base_url(i), headers=self.headers)
    soup = bs(response.content, 'html.parser')

    # find all properties shown on the webpage
    texts = soup.findAll('div', {'class' : 'propertyCard-wrapper'})
    for line in texts:
        # Obtain the link to each webpage containing a single listing
        link = line.find('a', {'class' : 'propertyCard-link'})['href']
        
        # Check to see that there is a link and it hasn't already been used
        if link != '' and link not in self.counted:
            # self.property_listings.iloc[len(self.property_listings),:] = None
            
            # Searching for house type, beds and baths
            prop_info = line.find('div', {'class': "property-information"})
            # self.property_listings.loc[len(self.property_listings)-1, 'property_type'] = 

            # <span class="propertyCard-moreInfoNumber">1/20</span>
            
            self.__populate_date_listed(line)

        # Add the link to the set so as to not repeat featured listings
        self.counted.add(link)



        # Set Nans to None 
        self.property_listings['url'=='Nan'] = None
        self.property_listings['image_url'=='Nan'] = None
        self.property_listings['title'=='Nan'] = None
        self.property_listings['price'=='Nan'] = None
    return

def split(date_info: str) -> tuple:
    """Reads in a string with date added info and whether it is new listing or reduced

    Args:
        date_info (str): _description_

    Returns:
        tuple: _description_
    """
    # Regex options
    add_type = {"reduced", "added"}
    recent_add = {"today", "yesterday"}
    # Declare outputs
    found1 = None
    found2 = None
    # Make all lower case
    date_info = date_info.lower()
    # Form regex for type and search
    for tmp in add_type:
        if re.search(tmp, date_info) is not None:
            found1 = tmp
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
        
    
    # If the date is today or yesterday then replace with an actual date