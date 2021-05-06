
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


pp = pprint.PrettyPrinter()

# loading existing records
df_cities = pd.read_csv(str(Path(os.getcwd()).parent)+'\\db\\booking.com_reference_table_list_cities.csv')
df_countries = pd.read_csv(str(Path(os.getcwd()).parent)+'\\db\\booking.com_reference_table_list_countries.csv')

headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
base_url = 'https://www.booking.com/'

label = 'gen173nr-1DCAEoggJCAlhYSDNYBGiTAYgBAZgBLsIBCndpbmRvd3MgMTDIAQzYAQPoAQGSAgF5qAID'
sid ='9a8c5833856fc2a673c8768cd752f3d1'
sb =1
src='searchresults'
src_elem='sb'



from class_function_available_listings import get_available_listings_per_place_backend

class Bookingcom:
    
    def __init__(self):
        self.url = None
    
    def get_all_listing_per_country(self,country_name):
        pass
    
    
    def get_available_listings_per_country(self,country_name,checkin_date,checkout_date):
        dest_type = 'country'
        df_listings_available = get_available_listings_per_place_backend(self,place_name,checkin_date,checkout_date,dest_type)
        return df_listings_available
    
    def get_available_listings_per_city(self,city_name,checkin_date,checkout_date):
        dest_type = 'city'
        df_listings_available = get_available_listings_per_place_backend(self,place_name,checkin_date,checkout_date,dest_type)
        return df_listings_available
    
    
    def get_all_listing_per_city(self,city_name):
        url = (
    "https://www.booking.com/searchresults.en-gb.html"
    "?aid=304142&sb={sb}&src={src}"
    "&ss=Catania"
    "&is_ski_area=&ssne=Catania&ssne_untouched=Catania"
    "&checkin_year=2021&checkin_month=6&checkin_monthday=12"
    "&checkout_year=2021&checkout_month=6&checkout_monthday=15"
    "&group_adults=2&group_children=0"
    "&no_rooms=1&from_sf=1&ss_raw=Catania"
    "&ac_position=0&ac_langcode=en&ac_click_type=b&dest_id=-3378435&dest_type=city".format(
        label=label
        ,sid=sid
        ,sb=sb
        ,src=src))
        pass
    
    
if __name__=='__main__':
    bk = Bookingcom()
    t1 = time.perf_counter()
    place_name='Greenland'
    checkin_date = '2021-08-12'
    checkout_date = '2021-08-15'
    afg = bk.get_available_listings_per_country(place_name,checkin_date,checkout_date)
    print('-----------------------')
    t2 = time.perf_counter()
    print(f'Finished in {t2-t1} seconds')

    t1 = time.perf_counter()
    place_name='Nuuk'
    checkin_date = '2021-08-12'
    checkout_date = '2021-08-15'
    kabul = bk.get_available_listings_per_city(place_name,checkin_date,checkout_date)
    t2 = time.perf_counter()
    print(f'Finished in {t2-t1} seconds')
