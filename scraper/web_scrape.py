from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
from urllib.request import urlopen
import re
import requests

class rightmove_listings():
    '''
    This class provides the framework for scraping rightmove based on a region id and other optional information.
    '''
    def __init__(self):
        # Create a dictionary that contains all listing information to be held within a database for a single listing. This acts as a template for the list of listings
        self.property_listings = pd.DataFrame(columns = ['id', 'title', 'property_type', 'price', 'date_listed', 'reduced', 'bedrooms', 'bathrooms',
                        'tenure', 'description', 'url', 'image_url', 'region_id', 'postcode', 'num_images'])

    def attach_url(self, postcode = '', max_price = '', min_price = '', min_bedrooms = '', max_bedrooms = '', radius = ''):
        # A query must be made to rightmove to get the location identifier from the postcode that has been provided
        url = f"https://www.rightmove.co.uk/property-for-sale/search.html?searchLocation={postcode}"
        with urlopen(url) as response:
            # print(response)
            soup = bs(response, "html.parser")
            # print(soup.find('input', {"name": "locationIdentifier"})['value'])
            region_id = soup.find('input', {"name": "locationIdentifier"})['value'].split(sep="^")[1]
            # print(region_id)

        # Store the base url for the search results as a lambda function, allowing the cycling through the webpage
        self.base_url = lambda index: 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=OUTCODE%5E{}&minBedrooms={}&maxBedrooms={}&maxPrice={}&min_price={}&radius={}&index={}&propertyTypes=detached%2Csemi-detached%2Cterraced&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords='.format(region_id, min_bedrooms, max_bedrooms, max_price, min_price, radius, index)
        self.__number_of_listings()
        return
    
    def attach_url(self, url):
        # Set the objects base url
        self.base_url = lambda index: url
        self.__number_of_listings()
        return
    
    def __number_of_listings(self):
        '''
        Calculates the number of listings and sets the listings per page 
        '''
        with urlopen(self.base_url(1)) as response:
            soup = bs(response, 'html.parser')

            # number of listings
            self.nlistings = int(soup.find('span', {'class' : 'searchHeader-resultCount'}).string)
            # listings per page for rightmove
            self.nperpage = 24
        return

    def listing_links(self, page_num, region_id = None, postcode = None):
        '''
        Searches a particular index of listings depending on the result of the pagination.
        '''
        i = 1
        # num_listings = 23
        counted = set()
        while i <= self.nlistings:
            with urlopen(self.base_url(i)) as response:
                soup = bs(response, 'html.parser')

                # find all properties shown on the webpage
                texts = soup.findAll('div', {'class' : 'propertyCard-wrapper'})
                for line in texts:
                    # Obtain the link to each webpage containing a single listing
                    link = line.find('a', {'class' : 'propertyCard-link'})['href']
                    
                    # Check to see that there is a link and it hasn't already been used
                    if link != '' and link not in counted:
                        # self.property_listings.iloc[len(self.property_listings),:] = None
                        self.property_listings.loc[len(self.property_listings), 'url'] = 'https://rightmove.co.uk' + link
                        self.property_listings.loc[len(self.property_listings)-1, 'id'] = int(link.split('/')[2][:-1])
                        self.property_listings.loc[len(self.property_listings)-1, 'title'] = line.address.span.string
                        self.property_listings.loc[len(self.property_listings)-1, 'image_url'] = line.img['src']
                        self.property_listings.loc[len(self.property_listings)-1, 'price'] = int(''.join(re.findall(r'\d+', line.find('div', {'class' : 'propertyCard-priceValue'}).string)))
                        self.property_listings.loc[len(self.property_listings)-1, 'region_id'] = region_id
                        self.property_listings.loc[len(self.property_listings)-1, 'postcode'] = postcode
                        self.property_listings.loc[len(self.property_listings)-1, 'num_images'] = int(line.find('span', {'class' : 'propertyCard-moreInfoNumber'}).string.split('/')[0])

                        # <span class="propertyCard-moreInfoNumber">1/20</span>
                        
                        self.__populate_date_listed(line)

                    # Add the link to the set so as to not repeat featured listings
                    counted.add(link)
                    # print(self.property_listings)
            i += self.nperpage-1

            # Set Nans to None 
            self.property_listings['url'=='Nan'] = None
            self.property_listings['image_url'=='Nan'] = None
            self.property_listings['title'=='Nan'] = None
            self.property_listings['price'=='Nan'] = None
        return
    
    def __populate_date_listed(self, line):
        date_listed = line.find('span', {'class' : 'propertyCard-branchSummary-addedOrReduced'}).string
        # Try and populate the date listed field, if it fails for whatever reason, set equal to None for the database
        try:
            date_listed = date_listed.split()
            if date_listed[0] == 'Reduced':
                self.property_listings.loc[len(self.property_listings)-1, 'reduced'] = True
            else:
                self.property_listings.loc[len(self.property_listings)-1, 'reduced'] = False
            self.property_listings.loc[len(self.property_listings)-1, 'date_listed'] = datetime.strptime(date_listed[2], "%d/%m/%Y").date()
        except:
            self.property_listings.loc[len(self.property_listings)-1, 'reduced'] = False
            self.property_listings.loc[len(self.property_listings)-1, 'date_listed'] = None
            pass
    
    def listing_detail(self, detail_url):
        '''
        Returns dictionary of specific information about a given listing
        '''
        try:
            with urlopen(detail_url) as response:
                # A dictionary mapping to translate from some rightmove keywords in the html to the dataframe
                mapping = {'PROPERTY TYPE' : 'property_type', 'BEDROOMS': 'bedrooms', 'BATHROOMS' : 'bathrooms', 'TENURE': 'tenure'}
                mapping_set = set(mapping.keys())
                # Initialise the output variables. The model can be updated with detailed listing results
                images = []
                outs = dict() 

                soup = bs(response, 'html.parser')
                outs['description'] = soup.find('div', {'class' : 'STw8udCxUaBUMfOOZu0iL _3nPVwR0HZYQah5tkVJHFh5'}).div
                # Obtain property type, bedrooms, bathrooms etc.
                data = soup.find('div', {'class' : "_4hBezflLdgDMdFtURKTWh"})
                for element in data:
                    if element.dt.string in mapping_set:
                        outs[mapping[element.dt.string]] = element.dd.string
            
            # Now open the rightmove collage to obtain all of the images
            tmp_url = detail_url.split(sep='?')[0]+'media?'+detail_url.split(sep='?')[1]
            with urlopen(tmp_url) as response:
                # find the image urls
                soup = bs(response, 'html.parser')
                data = soup.findAll('meta', {'property' : 'og:image'})
                for dat in data:
                    images += [dat['content']]
            return outs, images
        except Exception as e:
            return e

    def get_listings(self):
        '''
        Returns the dictionary of listings found for a particular search criteria.
        '''
        return self.property_listings

if __name__ == "__main__":
    max_price = 600000
    min_price = ''
    min_bedrooms = ''
    region_id = 'yo1'
    max_bedrooms = '2'
    radius = '0.5'

    rightmove = rightmove_listings()
    rightmove.search_listings(region_id, max_price, min_price, min_bedrooms, max_bedrooms, radius)
    df = rightmove.get_listings()
