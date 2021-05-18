
import pandas as pd
import requests
import numpy as np
import pprint
from bs4 import BeautifulSoup
import re
import json 
import concurrent.futures
import time
import traceback
import itertools
import pandas as pd
import os
from pathlib import Path
import time
import cchardet

pp = pprint.PrettyPrinter()





from geofunctions import get_locality_from_address,reverse_geocoding
from class_function_available_listings import get_available_listings_per_place_backend

class Bookingcom:
    
    def __init__(self):
        self.url = None
    
    
    def get_available_listings_per_country(self,country_name,checkin_date,checkout_date):
        dest_type = 'country'
        df_listings_available = get_available_listings_per_place_backend(self,place_name,checkin_date,checkout_date,dest_type)
        return df_listings_available
    
    def get_available_listings_per_city(self,city_name,checkin_date,checkout_date):
        dest_type = 'city'
        df_listings_available = get_available_listings_per_place_backend(self,place_name,checkin_date,checkout_date,dest_type)
        return df_listings_available
    
    
    def get_available_listings_per_address(self,address,checkin_date,checkout_date):
        place_name = get_locality_from_address(address)
        exceptions = ['Multiple results','No place found']
        if place_name in exceptions:
            return None
        dest_type = 'city'
        df_listings_available = get_available_listings_per_place_backend(self,place_name,checkin_date,checkout_date,dest_type)
        return df_listings_available
    
    def get_available_listings_per_geolocation(self,lat,lng,checkin_date,checkout_date):
        place_name = reverse_geocoding(lat,lng)
        dest_type = 'city'
        df_listings_available = get_available_listings_per_place_backend(self,place_name,checkin_date,checkout_date,dest_type)
        return df_listings_available
    
        

