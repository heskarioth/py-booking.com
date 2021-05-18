
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

import os
from pathlib import Path

df_cities = pd.read_csv(str(Path(os.getcwd()).parent)+'\\db\\booking.com_reference_table_list_cities.csv')
df_countries = pd.read_csv(str(Path(os.getcwd()).parent)+'\\db\\booking.com_reference_table_list_countries.csv')


headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
base_url = 'https://www.booking.com/'


from url_creation_funcs import reference_table_creation_place_get_all_pages_urls_offsets,reference_table_creation_place_get_all_pages_urls_single_result
from content_page_extraction_utils import extract_data_from_listing

def get_available_listings_per_place_backend(self,place_name,checkin_date,checkout_date,dest_type=None):
    
    dest_place_id,number_listings = get_place_id_size(place_name,dest_type)

    if dest_place_id==0:
        return '"{}" was not found as a {}. Please make sure you typed it correctly.'.format(place_name,dest_type)
    
    checkin_year,checkout_month,checkout_monthday = generate_date_comb(checkin_date)
    checkout_year,checkout_month,checkout_monthday = generate_date_comb(checkout_date)
    
    offset_urls = reference_table_creation_place_get_all_pages_urls_offsets(number_listings,dest_place_id,dest_type,checkin_year,checkout_month,checkout_monthday,checkout_year,checkout_month,checkout_monthday)
    
    single_urls = reference_table_creation_place_get_all_pages_urls_single_result(offset_urls)
    
    single_urls = fix_single_urls_with_checkin_out_dates(single_urls,dest_place_id,dest_type,checkin_date,checkout_date)
    
    print('Total listings found in {} is {}'.format(place_name,len(single_urls)))
    single_dfs = extract_data_from_listing(single_urls,checkin_date,checkout_date)
    
    df_listings_available = list_dfs_to_single_df(single_dfs)
    
    print('Total listings available between your travel dates {}'.format(df_listings_available.shape[0]))
    return df_listings_available



#======================================================================================================
#part 1
#helper functions for : get_available_listings_per_place_backend
def get_place_id_size(place_name,dest_type=None):
    if dest_type=='country':
        return get_country_id_size(place_name)
    
    return get_city_id_size(place_name)


def get_country_id_size(country_name):
    try:
        dest_id_country,number_listings = df_countries[df_countries.country_name.str.lower().str.replace(' ','')==country_name.lower().replace(' ','')][['dest_id','number_listings']].values[0]
    except IndexError:
        dest_id_country,number_listings = (0,0)
        pass
    return dest_id_country,number_listings

def get_city_id_size(city_name):
    try:
        dest_id_city = df_cities[df_cities.city_name.str.lower().str.replace(' ','')==city_name.lower().replace(' ','')]['dest_id_city'].values[0]
        number_listings = check_n_listings_for_selected_city(dest_id_city)
    except IndexError:
        dest_id_city,number_listings = (0,0)
        pass
    return dest_id_city,number_listings

def check_n_listings_for_selected_city(dest_id):
    url = ("https://www.booking.com/searchresults.en-gb.html"
           "?aid=304142&sb=1&src=searchresults"
            "&group_adults=2&group_children=0"
            "&ac_position=0&ac_langcode=en&ac_click_type=b&dest_id={dest_id}&dest_type=city".format(
        dest_id=dest_id))
    #print(url)
    headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"}
    r = requests.get(url,headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    if ':' in soup.find('div',{'class':'sr_header'}).get_text().strip():
        number_listings = int(re.sub('\D+','',soup.find('div',{'class':'sr_header'}).get_text().strip()))
    else:
        number_listings = 0
    return number_listings


def generate_date_comb(date):
    date_string = ''.join(str(x) for x in re.findall('\d+',date))
    date_year = date_string[:4]
    date_month = date_string[4:6]
    date_monthday = date_string[6:8]
    return date_year,date_month,date_monthday



# other functions for extract_data_from_listing
def fix_single_urls_with_checkin_out_dates(single_urls,dest_place_id,dest_type,checkin_date,checkout_date):
    for idx in range(len(single_urls)):
        single_urls[idx] = single_urls[idx].split('aid=',1)[0]+'aid=304142&label=gen173nr-1FCAQoggJCDWNpdHlfLTIwODQ2MTVICVgEaFCIAQGYAQm4ARfIAQzYAQHoAQH4AQaIAgGoAgO4Aur8jYUGwAIB0gIkODEwNDA1OGUtNmU0Yy00ODNkLTk3NDUtOTgwZTljMjFkYTM42AIF4AIB&sid=1be0c5c347b9211a7db5d9bc410dd13a&dest_id={}&dest_type={}&group_adults=2&group_children=0&hapos=7&hpos=1&no_rooms=1&sr_order=popularity&srepoch=1621327467&srpvid=9fc23d75192101cc&ucfs=1&sig=v10S0SrADj&checkin={}&checkout={}'.format(dest_place_id,dest_type,checkin_date,checkout_date)
    single_urls = list(set(single_urls))
    return single_urls


#=========================================
#part 4 final parsing 
def list_dfs_to_single_df(single_dfs):
    df = pd.DataFrame()
    for idx in range(len(single_dfs)):
        df = pd.concat([df,single_dfs[idx]])
    #remove possible duplicates
    df = df.drop_duplicates(subset=['name','latitude','longitude'])
    return df
