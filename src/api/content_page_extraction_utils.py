
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
from collections import defaultdict


base_url = 'https://www.booking.com/'


def extract_data_from_listing(single_urls,checkin_date,checkout_date):
    
    def councurrency_extraction(single_url):
        df_hotel_details = pd.DataFrame()
        with requests.Session() as session:
            t1 = time.perf_counter()
            headers={"Content-Type": "application/json"
                     ,'Accept-Encoding': 'gzip, deflate'
                     ,"x-cache":"HIT","Connection": "keep-alive"
                    ,'User-Agent':"Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36"
                    }
            
            r = session.get(single_url,headers=headers)
            soup = BeautifulSoup(r.text, 'lxml')
            tmp = json.loads("".join(soup.find("script", {"type":"application/ld+json"}).contents))
            try:
                
                t1 = time.perf_counter()
                page_details = get_page_details_main(soup)
                t2 = time.perf_counter()
                hotel_details =  parse_hotel_location(tmp) #
            except IndexError:
                print('Error')
                print(single_url)
                traceback.print_exc()
                pass
            #if the hotel is not available for that given date, no point taking the details
            if page_details is not None:
                hotel_details.update(page_details)
            
        df_hotel_details = pd.concat([df_hotel_details,pd.DataFrame(hotel_details,index=[0])]) #
        
        return df_hotel_details
        
    single_dfs = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(councurrency_extraction, single_urls)
        for result in results:
            single_dfs.append(result)
           
    return single_dfs


#helper functions for extract_data_from_listing
def get_page_details_main(soup):

    availability_message = soup.find('div',{'id':'availability'}).find('div',{'class':'u-font-size:12 c-alert c-alert--red no_availability_banner_wrapper'})
    if availability_message is not None:
        no_availability_options = ['Sorry, this hotel has no rooms available for the dates of your stay','Sorry this property has no availability on our site for your dates',"Not available on our site – sorry, this property isn't available for the dates you selected."]
        if availability_message.get_text().strip() in no_availability_options:
            #print('No room available.')
            return None
    else:
        """
        Divs with class = js-rt-block-row hprt-table-cheapest-block hprt-table-cheapest-block-fix js-hprt-table-cheapest-block 
        Will tell you which room pricing option is the cheapest.
        The idea here is to go through each line (tr) of the table of Booking.com, store the values (which are accessed via
        td) we are interested in, and, when we find the class (tr), exit loop. In this way, the latest td you have scraped,
        will represent the cheapest available plan.

        """
        room_price = get_page_details_room_info(soup)
        
        #facilities included in the booking
        facilities_dict = get_page_details_facilities_list(soup)

        # get description hotel
        property_description = ''.join([str(x).strip().replace('<br/>','') for x in soup.find('div',{'class':'property_description_drawer__content'}).find('p').contents])

        # get ratings from hotel
        ratings = get_page_details_ratings(soup)
        
        ##hotel ammendity details
        ammendities_dict = get_page_details_ammendities(soup)
        
        #get hotel_ids
        hotel_ids_dict = get_page_details_hotel_ids(soup)
        
        #compile response object
        page_details = get_page_details_response_object(room_price,facilities_dict,property_description,ratings,ammendities_dict,hotel_ids_dict)

        return page_details


#-------------------------------------------------------------
#part 3.1 helper functions for get_page_details_main
def get_page_details_facilities_list(soup):

    for idx,script in enumerate(soup.find_all('script')):
        if 'b_booking_rooms_facilities' in str(script):
            
            #get room facilities
            data = re.search(r'b_booking_rooms_facilities:.*(.*?)',(soup.find_all('script')[idx]).contents[0]).group(0).replace('b_booking_rooms_facilities: ','')[:-1]
            facilities = json.loads(data)
            facilities_dict = {}
            for key_f in facilities.keys():
                for f in facilities[key_f]:
                    facilities_dict[f['name']]=f['highlighted']
            facilities_dict = {'Facility_'+facility:value for facility,value in facilities_dict.items()}
            return facilities_dict
    return {}



def get_page_details_room_info(soup):
    for idx,script in enumerate(soup.find_all('script')):
        if 'b_room_blocks_json' in str(script):
            data = re.search(r'b_room_blocks_json:.*(.*?)',(soup.find_all('script')[idx]).contents[0]).group(0).replace('b_room_blocks_json: ','')[:-1]
            data = json.loads(data)
            list_indexes = list(data.keys())

            #get all bookings available for that hotel
            room_price_info = defaultdict(dict)
            for idx in range(len(list_indexes)):
                room = data[list_indexes[idx]]
                room_price_info[idx]['pricePerNight'] = room['pricePerNight']
                room_price_info[idx]['price'] = room['price']
                room_price_info[idx]['maxPersons'] = room['maxPersons']
                room_price_info[idx]['roomName'] = room['roomName']
                room_price_info[idx]['maxPersons'] = room['maxPersons']
                if 'preferences' in room.keys():
                    if 'bedPreference' in room['preferences']:
                        bed_type_option_given_price = []
                        for _ in range(len(room['preferences']['bedPreference'])):
                            bed_type = room['preferences']['bedPreference'][_]
                            for i in range(len(bed_type['bed_type'])):
                                bed_type_option_given_price.append(bed_type['bed_type'][i].get('name_withnumber'))
                        room_price_info[idx]['bedType'] = "~".join([room for room in bed_type_option_given_price])

            #save the cheapest one as single response, wrap together the rest
            series_p = pd.Series(dtype=np.float64)
            for dict_idx in room_price_info:
                series_p = pd.concat([series_p,pd.Series(room_price_info[dict_idx]['price'],index=[dict_idx],dtype=np.float64)])
            best_priced_room = room_price_info[series_p.idxmin()]['pricePerNight']
            best_priced_room_info= json.dumps(room_price_info[series_p.idxmin()])
            all_priced_rooms = json.dumps(room_price_info)
            return {'best_priced_room':best_priced_room,'best_priced_room_info':best_priced_room_info,'all_priced_rooms':all_priced_rooms}
        
def get_page_details_ratings(soup):
    # get ratings from hotel
    n_ratings = len(soup.find_all('div',{'class':'c-score-bar'}))
    ratings = {}
    for idx in range(n_ratings):
        rating_name = soup.find_all('div',{'class':'c-score-bar'})[idx].span.get_text()
        ratings['Rating_'+rating_name]=soup.find_all('div',{'class':'c-score-bar'})[idx].find('span',{'class':'c-score-bar__score'}).get_text()
    return ratings


def get_page_details_ammendities(soup):
    
    ammendities = []
    objects = [('div',{'class':'bui-list__body'}),('span',{'class':'facilities__summary__name'})]
    for object_single in objects:
        ammendities_m_hp_accordion__shorttext = soup.find('div',{'id':'facilities'}).find('div',{'class':'m_hp_accordion__shorttext'}).find_all(object_single)
        if (len(ammendities_m_hp_accordion__shorttext))>0:
            break
    for idx in range(len(ammendities_m_hp_accordion__shorttext)):
        ammendities.append(ammendities_m_hp_accordion__shorttext[idx].get_text().strip())
    ammendities = [ammendity for ammendity in ammendities if len(ammendity)>0]

#     if (soup.find('ul',{'class':'hp-facility-columns js-hp-facility-columns m_hp_facilites_wrapper bui-list bui-list--text bui-list--divided'})) is not None:
#         for category in (soup.find('ul',{'class':'hp-facility-columns js-hp-facility-columns m_hp_facilites_wrapper bui-list bui-list--text bui-list--divided'}).find_all('li',{'class':'bui-list__item'})):    
#             try:
#                 for subcategory in category.find_all('div',{'class':'bui-list__body'}):
#                     main_category = (category.find('div',{'class':'m_hp_facilities_heading'}).text.strip().replace('\n',''))
#                     subcategory = (subcategory.text.strip().replace('\n',' '))
#                     ammendities.append('{}__{}'.format(main_category,subcategory))
#             except AttributeError as attr:
#                 pass
#     else:
#         for main_category in (soup.find('div',{'class':'facilities__body'})).find_all('h4',{'class':'facilities__group__title'}):
#             for sub_category in (soup.find('div',{'class':'facilities__body'})).find_all('li',{'class':'facilities__item facilities__item--legacy'}):
#                 ammendities.append('{}__{}'.format(main_category.text,sub_category.span.getText().strip()))

    ammendities = ['Ammendity_'+ammendity for ammendity in ammendities]
    ammendities_dict = {ammendity:1 for ammendity in ammendities}
    return ammendities_dict

def get_page_details_hotel_ids(soup):
    #find which script has the info we need and take the index
    for idx,script in enumerate(soup.find_all('script')):
        if 'b_hotel_id' in str(script):
            break
    #get hotel id
    hotel_id = int(re.search(r'b_hotel_id: .*(.*?)',(soup.find_all('script')[idx]).contents[0]).group(0).replace('b_hotel_id: ','')[:-1].replace('\'',''))  
    #get stid
    stid = int(re.search(r'b_stid: .*(.*?)',(soup.find_all('script')[idx]).contents[0]).group(0).replace('b_stid: ','')[:-1].replace('\'',''))
    hotel_ids_dict = {'hotel_id':hotel_id,'stid':stid}
    return hotel_ids_dict


def get_page_details_response_object(room_price,facilities_dict,property_description,ratings,ammendities_dict,hotel_ids_dict):
    page_details = {}
    page_details.update(room_price)
    page_details.update(ratings)
    page_details.update(hotel_ids_dict)
    page_details.update({'property_description':property_description})
    page_details.update(facilities_dict)
    page_details.update(ammendities_dict)
    
    return page_details
#-------------------------------------------------------------------------------
# part 3.2 helper function for parse_hotel_location

def parse_hotel_location(hotel_details):
    hotel_location = {
        
        'name':hotel_details['name']
        ,'aggregateRating_bestRating':check_json_value_nested_value(hotel_details,'aggregateRating','bestRating')
        ,'aggregateRating_ratingValue':check_json_value_nested_value(hotel_details,'aggregateRating','ratingValue')
        ,'aggregateRating_type':check_json_value_nested_value(hotel_details,'aggregateRating','@type')
        ,'aggregateRating_reviewCount':check_json_value_nested_value(hotel_details,'aggregateRating','reviewCount')
        ,'latitude':get_lat_long(hotel_details)[0]
        ,'longitude':get_lat_long(hotel_details)[1]
        ,'@type':hotel_details['@type']
        
        #,'priceRange':hotel_details['priceRange']
        ,'priceRange': None if hotel_details['priceRange'] is None else re.search('\d+',hotel_details['priceRange']).group()
        ,'hasMap':hotel_details['hasMap']
        ,'description':hotel_details['description']
        ,'url':hotel_details['url']
        ,'image':hotel_details['image']
        ,'address_streetAddress':hotel_details['address']['streetAddress']
        ,'address_addressCountry':hotel_details['address']['addressCountry']
        ,'address_addressRegion':hotel_details['address']['addressRegion']
        
    } 
    return hotel_location
    
def check_json_value(json_response,key_response):
    """ Helper function to check if json_response has expected value"""
    dict_parsed = {}
    try:
        dict_parsed[key_response] = json_response[key_response]
    except KeyError as k:
        dict_parsed[key_response] = np.nan
    return dict_parsed[key_response]
    

def check_json_value_nested_value(json_response,key_response_l1,key_response_l2):
    """ Helper function to check if json_response has expected value"""
    dict_parsed = {}
    try:
        dict_parsed[key_response_l1] = json_response[key_response_l1][key_response_l2]
    except KeyError as k:
        dict_parsed[key_response_l1] = np.nan
    return dict_parsed[key_response_l1]

def get_lat_long(hotel_details):
    """
    Input: hotel_details - dict containing google maps address
    Output: parsed lat-long coordinates ( as tuples)
    """
    coordinates = re.findall('[-]?[\d]+[.][\d]*',hotel_details['hasMap'])
    latitude,longitude = coordinates[:2]
    return latitude,longitude
