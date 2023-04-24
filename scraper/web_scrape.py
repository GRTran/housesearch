from bs4 import BeautifulSoup as bs
import pandas as pd
from urllib.request import urlopen

class rightmove_listings():
    '''
    This class provides the framework for scraping rightmove based on a region id and other optional information.
    '''
    def __init__(self, region_id = '5E1296', max_price = '', min_price = '', min_bedrooms = '', max_bedrooms = '', radius = ''):
        # Store the base url for the search results as a lambda function, allowing the cycling through the webpage
        self.base_url = lambda index: 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%{}&minBedrooms={}&maxBedrooms={}&maxPrice={}&min_price={}&radius={}&index={}&propertyTypes=detached%2Csemi-detached%2Cterraced&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords='.format(region_id, min_bedrooms, max_bedrooms, max_price, min_price, radius, index)

        # Create a dictionary that contains all listing information to be held within a database for a single listing. This acts as a template for the list of listings
        # self.single_listing = pd.Series({'title', 'property type', 'price', 'bedrooms', 'bathrooms',
        #                 'tenure', 'description', 'url', 'image_url'})
        self.property_listings = pd.DataFrame(columns = ['title', 'property type', 'price', 'bedrooms', 'bathrooms',
                        'tenure', 'description', 'url', 'image_url'])
        # print(self.property_listings)
        # Create a dictionary that will contain the rightmove listings
        self.__number_of_listings()
        self.__listing_links()
        self.__listing_information()

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

    def __listing_links(self):
        '''
        Gets each individual listing url and stores it in the dict structure defined within __init__
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
                        self.property_listings.loc[len(self.property_listings), 'url'] = 'https://rightmove.co.uk' + link
                    # Add the link to the set so as to not repeat featured listings
                    counted.add(link)
            i += self.nperpage-1
        # print(self.property_listings)
        return
    
    def __listing_information(self):
        '''
        Populates the pandas.Dataframe with the listing information
        '''
        
        # A dictionary mapping to translate from some rightmove keywords in the html to the dataframe
        mapping = {'PROPERTY TYPE' : 'property type', 'BEDROOMS': 'bedrooms', 'BATHROOMS' : 'bathrooms', 'TENURE': 'tenure'}
        mapping_set = set(mapping.keys())

        # Iterate through each link, opening it and extracting all the relevant listing information
        for i, link in enumerate(self.property_listings['url']):
            # for each of the links open them and extract necessary data
            with urlopen(link) as response:
                soup = bs(response, 'html.parser')
                self.property_listings.loc[i, 'title'] = soup.find('h1', {'itemprop' : 'streetAddress'}).string
                self.property_listings.loc[i, 'price'] = soup.find('div', {'class' : '_1gfnqJ3Vtd1z40MlC0MzXu'}).span.string
                self.property_listings.loc[i, 'description'] = soup.find('div', {'class' : 'STw8udCxUaBUMfOOZu0iL _3nPVwR0HZYQah5tkVJHFh5'}).div

                data = soup.find('div', {'class' : "_4hBezflLdgDMdFtURKTWh"})
                for element in data:
                    if element.dt.string in mapping_set:
                        self.property_listings.loc[i, mapping[element.dt.string]] = element.dd.string
        print(self.property_listings)
        return
    
    def get_listings(self):
        '''
        Returns the dictionary of listings found for a particular search criteria.
        '''
        return self.property_listings

if __name__ == "__main__":
    max_price = 600000
    min_price = ''
    min_bedrooms = ''
    region_id = '5E1296'
    max_bedrooms = '2'
    radius = '0.5'

    rightmove = rightmove_listings(region_id, max_price, min_price, min_bedrooms, max_bedrooms, radius)
