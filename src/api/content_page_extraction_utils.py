
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


def extract_data_from_listing(single_urls,checkin_date,checkout_date):
    
    def councurrency_extraction(single_url):
        df_hotel_details = pd.DataFrame()
        r = requests.get(single_url,headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        tmp = json.loads("".join(soup.find("script", {"type":"application/ld+json"}).contents))
        try:
            page_details = get_page_details_main(soup)
            hotel_details = parse_hotel_location(tmp)
        except IndexError:
            print('Error')
            print(single_url)
            traceback.print_exc()
            pass
        #if the hotel is not available for that given date, no point taking the details
        if page_details is not None:
            hotel_details.update(page_details)
        else:
            #print('"{}" in {} has no rooms available during your travel period.\nCheck other dates at: {}\n-------------------------------------------------------------------------'.format(hotel_details['name'],hotel_details['address_streetAddress'],single_url))
            pass
            
        df_hotel_details = pd.concat([df_hotel_details,pd.DataFrame(hotel_details,index=[0])])
        #df_hotel_details = pd.DataFrame(hotel_details,index=[0])
        return df_hotel_details
        
    single_urls = fix_single_urls_with_checkin_out_dates(single_urls,checkin_date,checkout_date)
    single_dfs = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(councurrency_extraction, single_urls)
        for result in results:
            single_dfs.append(result)
            
    return single_dfs

#helper functions for extract_data_from_listing
def get_page_details_main(soup):
    
    availability_message = (soup.find('div',{'id':'no_availability_msg'}))
    if availability_message is not None:
        if availability_message.span.get_text().strip()=='Sorry, this hotel has no rooms available for the dates of your stay':
            return None
    else:
        """
        Divs with class = js-rt-block-row hprt-table-cheapest-block hprt-table-cheapest-block-fix js-hprt-table-cheapest-block 
        Will tell you which room pricing option is the cheapest.
        The idea here is to go through each line (tr) of the table of Booking.com, store the values (which are accessed via
        td) we are interested in, and, when we find the class (tr), exit loop. In this way, the latest td you have scraped,
        will represent the cheapest available plan.

        """
        body = soup.find('table').find('tbody') #set up the body

        for tr in body.find_all('tr'): #per row

            for td in (tr('td',{'class':'hprt-table-cell -first hprt-table-cell-roomtype droom_seperator'})):

                #room name and bed type
                room_type = (td.find('span',{'class':'hprt-roomtype-icon-link'}).get_text().strip())
                room_bed_type = get_page_details_room_bed_type(td)

                #facilities included in the booking
                facilities_dict = get_page_details_facilities_list(td)

                #get room price
                potential_room_price_divs = ['bui-price-display__value prco-inline-block-maker-helper prco-f-font-heading','bui-price-display__value prco-text-nowrap-helper prco-inline-block-maker-helper prco-f-font-heading']
                
                
                #room_price = get_page_details_room_price_occupancy(tr,'bui-price-display__value prco-text-nowrap-helper prco-inline-block-maker-helper prco-f-font-heading')
                room_price = get_page_details_room_price_occupancy(tr,potential_room_price_divs)
                
                #get room occupancy
                potential_room_occupancy_divs = ['c-occupancy-icons hprt-occupancy-occupancy-info']
                room_occupancy = get_page_details_room_price_occupancy(tr,potential_room_occupancy_divs)

            #check that we got the numbers from the cheapest block; if so, exit loop.
            try:
                if 'js-hprt-table-cheapest-block' in tr.get('class'):
                    break
            except TypeError:
                pass

        # get description hotel
        property_description = soup.find('div',{'id':'property_description_content'}).get_text().strip()

        # get ratings from hotel
        ratings = get_page_details_ratings(soup)

        ##hotel ammendity details
        ammendities_dict = get_page_details_ammendities(soup)

        #get hotel_ids
        hotel_ids_dict = get_page_details_hotel_ids(soup)

        #compile response object
        page_details = get_page_details_response_object(room_price,room_type,room_bed_type,room_occupancy,property_description,facilities_dict,ammendities_dict,ratings,hotel_ids_dict)

        return page_details


#-------------------------------------------------------------
#part 3.1 helper functions for get_page_details_main
def get_page_details_room_bed_type(td):
    #get the bed type
    try:
        if (td.find('li',{'class':'rt-bed-type'})) is not None:
            room_bed_type = (td.find('li',{'class':'rt-bed-type'}).span.get_text().strip())
        else:
            room_bed_type = td.find('span',{'class':'hprt-roomtype-icon-link'}).get_text().strip()
    except AttributeError:
        room_bed_type = td.find('li',{'class':'bedroom_bed_type'}).get_text().strip()
    return room_bed_type

def get_page_details_facilities_list(td):
    """
    Input: td - column from soupe table.
    Output: list of facilities for that room option.
    """
    facilities_list = []
    for idx in range(len(td.find('div',{'class':'hprt-facilities-block'}).find_all('div',{'class':'hprt-facilities-facility'}))):
        facilities_list.append(td.find('div',{'class':'hprt-facilities-block'}).find_all('div',{'class':'hprt-facilities-facility'})[idx].span.get_text().strip())
    
    #sometimes, listings don't have facilities listed under section 'others'. We check if that is the case, if not. Extract data.
    if (td.find('ul',{'class':'hprt-facilities-others'})) is not None:
        n_loops =len(td.find('ul',{'class':'hprt-facilities-others'}).find_all('span',{'class':'hprt-facilities-facility'}))
        for idx in range(n_loops):
            facilities_list.append(td.find('ul',{'class':'hprt-facilities-others'}).find_all('span',{'class':'hprt-facilities-facility'})[idx].span.get_text().strip())

    facilities_list = ['Facility_'+facility for facility in facilities_list]
    facilities_dict= {facility:1 for facility in facilities_list}

    return facilities_dict

def get_page_details_room_price_occupancy(tr,div_classes):
    """
    Input: 
    - tr -> of soupe table
    - div_class -> class to inspect in loop function
    Output:
    If div_class = bui-price-display__value prco-text-nowrap-helper prco-inline-block-maker-helper prco-f-font-heading
       function will return room_price
    If div_class = c-occupancy-icons hprt-occupancy-occupancy-info
       function will return room_occupancy
    """
    for _ in range(len(tr.find_all('td'))):
        for div_class in div_classes:
            parsed_value = tr.find_all('td')[_].find('div',{'class':div_class})
            if parsed_value is not None:
                try:
                    output_value = (parsed_value.span.get_text().strip())
                except AttributeError:
                    output_value = (parsed_value.get_text().strip())
    return output_value

def get_page_details_ratings(soup):
    # get ratings from hotel
    n_ratings = len(soup.find_all('div',{'class':'c-score-bar'}))
    ratings = {}
    for idx in range(n_ratings):
        rating_name = soup.find_all('div',{'class':'c-score-bar'})[idx].span.get_text()
        ratings['Rating_'+rating_name]=soup.find_all('div',{'class':'c-score-bar'})[idx].find('span',{'class':'c-score-bar__score'}).get_text()
    return ratings

def get_page_details_ammendities(soup):
    ##hotel ammendity details
    ammendities = [] 
    for element in soup.find_all('div',{'class':'important_facility'}):
        ammendities.append(element.get('data-name-en'))

    ammendities = ['Ammendity_'+ammendity for ammendity in ammendities]
    ammendities_dict = {ammendity:1 for ammendity in ammendities}
    return ammendities_dict

def get_page_details_hotel_ids(soup):
    possible_location_script = [(soup.find_all('script',type="text/javascript"))[3],(soup.find_all('script',type="text/javascript"))[0]]
    for idx in range(len(soup.find_all('script'))):
        for script in possible_location_script:
            try:
                pattern = re.compile('hotel_id.*:.*\d+')
                hotel_id = re.findall(pattern, script.string)[0].strip().replace('\'','')#.strip().split(':')[1].strip()
                pattern = re.compile('stid.*:.*\d+')
                stid = re.findall(pattern, script.string)[0].strip().replace('\'','').strip().split(':')[1].strip()
                pattern = re.compile('dest_id.*:.*\d+')
                dest_id = re.findall(pattern, script.string)[0].strip().replace('\'','').strip().split(':')[1].strip()
                break
            except IndexError:
                pass

    hotel_ids_dict = {'hotel_id':hotel_id,'stid':stid,'dest_id':dest_id}
    return hotel_ids_dict

def get_page_details_response_object(room_price,room_type,room_bed_type,room_occupancy,property_description,facilities_dict,ammendities_dict,ratings,hotel_ids_dict):
    # combine all together in one single dict
    page_details = {
     'room_price':room_price
     ,'room_type':room_type
     ,'room_type_bed':room_bed_type
     ,'room_occupancy':room_occupancy
     ,'property_description':property_description
    }
    page_details.update(facilities_dict)
    page_details.update(ammendities_dict)
    page_details.update(ratings)
    page_details.update(hotel_ids_dict)
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
        ,'priceRange':hotel_details['priceRange']
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
#-------------------------------------------------------------------------------

# other functions for extract_data_from_listing
def fix_single_urls_with_checkin_out_dates(single_urls,checkin_date,checkout_date):
    for idx in range(len(single_urls)):
        single_urls[idx] = single_urls[idx].replace('&from=searchresults;highlight_room=#hotelTmpl','&checkin={}&checkout={}'.format(checkin_date,checkout_date))
        single_urls[idx] = str(re.sub(';highlight_room=.*','',single_urls[idx]))+'&checkin={}&checkout={}'.format(checkin_date,checkout_date)
    single_urls = list(set(single_urls))
    return single_urls
