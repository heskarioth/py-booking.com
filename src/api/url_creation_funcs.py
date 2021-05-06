
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

headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
base_url = 'https://www.booking.com/'

#part 2
# helper functions to get all urls
def reference_table_creation_place_get_all_pages_urls_offsets(number_listings,dest_place_id,dest_type,checkin_year=None,checkin_month=None,checkin_monthday=None,checkout_year=None,checkout_month=None,checkout_monthday=None):
    label = 'gen173nr-1DCAEoggJCAlhYSDNYBGiTAYgBAZgBLsIBCndpbmRvd3MgMTDIAQzYAQPoAQGSAgF5qAID'
    sid ='9a8c5833856fc2a673c8768cd752f3d1'
    src='searchresults'
    src_elem='sb'
    listings_per_page = 25
    n_pages = int(np.floor(number_listings/listings_per_page))
    offsets = [x * listings_per_page for x in range(n_pages+1)] + [number_listings - 3]
    list_urls = []
    for offset in offsets:
        url = (
            "https://www.booking.com/searchresults.en-gb.html"
            "?aid=304142&sb=1"
            "&checkin_year={checkin_year}&checkin_month={checkin_month}&checkin_monthday={checkin_monthday}"
            "&checkout_year={checkout_year}&checkout_month={checkout_month}&checkout_monthday={checkout_monthday}"
            "&ac_langcode=en&dest_id={dest_place_id}&dest_type={dest_type}&rows=25&offset={offset}".format(
                label=label
                ,sid=sid
                ,dest_place_id=dest_place_id
                ,dest_type=dest_type
                ,checkin_year=checkin_year,checkin_month=checkin_month,checkin_monthday=checkin_monthday
                ,checkout_year=checkout_year,checkout_month=checkout_month,checkout_monthday=checkout_monthday
                ,offset=offset
            ))
        list_urls.append(url)
    return list(set(list_urls))
    

def reference_table_creation_place_get_all_pages_urls_single_result(list_urls):
    
    def concurrency_get_single_urls(url):
        single_urls = []
        r = requests.get(url,headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        n_results = len(soup.find_all('a',{'class':'js-sr-hotel-link hotel_name_link url'}))
        
        for idx in range(n_results):
            href = (soup.find_all('a',{'class':'js-sr-hotel-link hotel_name_link url'})[idx].get('href').replace('\n',''))
            single_urls.append(base_url+href)
        return (single_urls)
    
    single_urls = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(concurrency_get_single_urls, list_urls)
        for result in results:
            single_urls.append(result)
    
    single_urls = (list(itertools.chain.from_iterable(single_urls)))
    return single_urls


#==================================================================================================================


