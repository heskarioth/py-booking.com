# py-booking.com
> Booking.com refused to grant me access to their API. <br>
> No problem. <br>
> I decided to build my own.<br>

## Table of contents
* [General Info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Usage Examples](#usage-examples)
* [Response Example](#response-examples)
* [Features](#features)
* [Status](#status)


## General Info
After building an automated end-to-end video hosting website (using Python for backend automation and WordPress for content management system), I have decided to start another side project. Essentially, I want to build a web app that, given my current location (gps coordinates or input location), will find me the cheapest accommodation (airbnb, hostel, spareroom, hotel, you name it) nearby based on different criterias like date, price range, etc. Ideally the website will comprise 5-6 different accommodation providers; currently in the works we have: airbnb, hostelworld and booking.com data. I'm planning on developing the front-end in Angular (in which, I have no prior experience) and have python jobs on the backend for search logic, backend and data retrieval (essentially, everything except the front end). I have already developed an api for hostelworld and the pipeline logic to extract data from airbnb.com as well.<br>
I was missing booking.com, which is what this repo is about.<br>

After browsing the web, I have found that, conversely to airbnb/hostelworld, booking.com does have an API for users. Naturally, I felt enthusiastic at the thought that I could simply use their API to get the data I needed.<br>

But wait. Not so fast. After applying to get access to their API, I received an automated rejection email (similar to the ones I kept getting back in university when applying for jobs).

![RejectedBooking.comAPI](imgs/bookingcomAPI.PNG)

No problem buddy. I decided to build my own. 

Lastly, I haven't found any unofficial booking.com API here in GitHub. So yes, feel free to steal whatever you need. Figuring out the right Requests parameters and div classes structure to scrape did take me a while, no need for you to do the same. Enjoy.

PS
<i>'Cheapest accommodation near me'</i> represents the MVP idea. Ideally I want to extend this project and turn it into a fully fledge trip planner capable of suggest me best places to stay based on number of days I want to stay in a given city, distance I want to travel, money budget, attractions I want to see and more. Stay tuned.

## Technologies
The code is written in python using Beatifulsoup and multithreading to boost up response time.

## Setup
- After cloning the repo. pip install the requirements.txt.
- Following the above changes, you can execute the script via terminal: python bookingcom.py

## Usage Examples
Instantiate the class
```python
hw = Bookingcom()
```
Show me all the hotels in Greenland between 12th and 15th August. Always want to go to Greenland and I heard that summer is the best time with highs hitting 9.5°C. Let's see.
```python
country_name ='Greenland'
checkin_date = '2021-08-12'
checkout_date = '2021-08-15'
bk.get_available_listings_per_country(country_name,checkin_date,checkout_date)
```
![GetAvailableListingsPerCountry](imgs/GetAvailableListingsPerCountry.PNG)

Interesting, what if we only want to check out the city of Nuuk?
```python
city_name ='Nuuk'
checkin_date = '2021-08-12'
checkout_date = '2021-08-15'
bk.get_available_listings_per_city(city_name,checkin_date,checkout_date)
```
![HostelByCityName](imgs/GetAvailableListingsPerCity.PNG)


## Response Example
Below a sample response body. Number of columns tend to vary but the average is roughly of 150-200 columns.
```json{"name": "2 Bedroom Duplex Apartment",
 "aggregateRating_bestRating": 0.0,
 "aggregateRating_ratingValue": 0.0,
 "aggregateRating_type": 0,
 "aggregateRating_reviewCount": 0.0,
 "latitude": "-18.1115906",
 "longitude": "178.4757184",
 "@type": "Hotel",
 "priceRange": "Prices for upcoming dates start at £83 per night (We Price Match)",
 "hasMap": "https://maps.googleapis.com/maps/api/staticmap?sensor=false&markers=color:blue%7c-18.1115906,178.4757184&zoom=15&size=1600x1200&center=-18.1115906,178.4757184&client=gme-booking&channel=booking-frontend&signature=HB-tmv1CN1eLf4pD5RqA2Wxlmr4=",
 "description": "Featuring air-conditioned accommodation with a terrace, 2 Bedroom Duplex Apartment is located in Suva.",
 "url": "https://www.booking.com/hotel/fj/2-bedroom-duplex-apartment.en-gb.html",
 "image": "https://cf.bstatic.com/images/hotel/max500/273/273445692.jpg",
 "address_streetAddress": "Koki Lane Laucala Beach Estate, Suva, Fiji",
 "address_addressCountry": "Fiji",
 "address_addressRegion": "Viti Levu",
 "room_price": "£249",
 "room_type": "Three-Bedroom Apartment",
 "room_type_bed": "Three-Bedroom Apartment",
 "room_occupancy": "×\n6",
 "property_description": "Featuring air-conditioned accommodation with a terrace, 2 Bedroom Duplex Apartment is located in Suva. This apartment features a garden and free private parking.\nThis apartment comes with 3 bedrooms, a kitchen with a microwave and a fridge, a flat-screen TV, a seating area and 2 bathrooms equipped with a shower.\nThe apartment offers a barbecue. A car rental service is available at 2 Bedroom Duplex Apartment.\nThe nearest airport is Nausori International Airport, 7.5 miles from the accommodation.",
 "Facility_Sea view": 1.0,
 "Facility_Garden view": 1.0,
 "Facility_Inner courtyard view": 1.0,
 "Facility_Air conditioning": 1.0,
 "Facility_Flat-screen TV": 1.0,
 "Facility_Terrace": 1.0,
 "Facility_Kitchen": 1.0,
 "Facility_Safety deposit box": 1.0,
 "Facility_Washing machine": 1.0,
 "Facility_Toilet": 1.0,
 "Facility_Sofa": 1.0,
 "Facility_Bath or shower": 1.0,
 "Facility_Towels": 1.0,
 "Facility_Linen": 1.0,
 "Facility_Socket near the bed": 1.0,
 "Facility_Tile/marble floor": 1.0,
 "Facility_Desk": 1.0,
 "Facility_Children's high chair": 1.0,
 "Facility_Seating Area": 1.0,
 "Facility_Private entrance": 1.0,
 "Facility_TV": 1.0,
 "Facility_Refrigerator": 1.0,
 "Facility_Ironing facilities": 1.0,
 "Facility_Tea/Coffee maker": 1.0,
 "Facility_Iron": 1.0,
 "Facility_Microwave": 1.0,
 "Facility_Kitchenware": 1.0,
 "Facility_Kitchenette": 1.0,
 "Facility_Fan": 1.0,
 "Facility_Additional toilet": 1.0,
 "Facility_Electric kettle": 1.0,
 "Facility_Tumble dryer": 1.0,
 "Facility_Wardrobe or closet": 1.0,
 "Facility_Oven": 1.0,
 "Facility_Stovetop": 1.0,
 "Facility_Toaster": 1.0,
 "Facility_Dining area": 1.0,
 "Facility_Dining table": 1.0,
 "Facility_Upper floors accessible by stairs only": 1.0,
 "Facility_Clothes rack": 1.0,
 "Facility_Drying rack for clothing": 1.0,
 "Ammendity_Family Rooms": 1.0,
 "Ammendity_Free Parking": 1.0,
 "hotel_id": "6834719",
 "stid": "304142",
 "dest_id": "6834719",
 "Facility_Ensuite bathroom": 0.0,
 "Facility_Soundproofing": 0.0,
 "Facility_Hardwood or parquet floors": 0.0,
 "Facility_Mosquito net": 0.0,
 "Facility_Satellite channels": 0.0,
 "Facility_Dressing room": 0.0,
 "Facility_Towels/sheets (extra fee)": 0.0,
 "Facility_Outdoor dining area": 0.0,
 "Facility_Cable channels": 0.0,
 "Facility_Entire unit located on ground floor": 0.0,
 "Facility_Toilet paper": 0.0,
 "Facility_Board games/puzzles": 0.0,
 "Facility_Books, DVDs, or music for children": 0.0,
 "Ammendity_Non Smoking Rooms": 0.0,
 "Ammendity_Wireless Lan": 0.0,
 "Ammendity_Coffee/Tea maker": 0.0,
 "Ammendity_Bar": 0.0,
 "Ammendity_breakfast": 0.0,
 "Rating_Staff": 0,
 "Rating_Location": 0,
 "Rating_Cleanliness": 0,
 "Rating_Value for money": 0,
 "Rating_Comfort": 0,
 "Rating_Facilities": 0,
 "Rating_Free WiFi": 0,
 "Facility_Balcony": 0.0,
 "Facility_Private bathroom": 0.0,
 "Facility_Free WiFi": 0.0,
 "Facility_Cleaning products": 0.0,
 "Facility_Interconnected room(s) available": 0.0,
 "Facility_Hairdryer": 0.0,
 "Facility_Outdoor furniture": 0.0,
 "Facility_Private apartment in building": 0.0,
 "Ammendity_Airport Shuttle": 0.0,
 "Ammendity_Free WiFi Internet Access Included": 0.0,
 "Rating_Cleanliness": 0,
 "Rating_Value for money": 0,
 "Rating_Comfort": 0,
 "Rating_Facilities": 0,
 "Rating_Free WiFi": 0,
 "Facility_366 feet²": 0.0,
 "Facility_City view": 0.0,
 "Facility_Free toiletries": 0.0,
 "Facility_Shower": 0.0,
 "Facility_Bathrobe": 0.0,
 "Facility_Slippers": 0.0,
 "Facility_Telephone": 0.0,
 "Facility_iPod dock": 0.0,
 "Facility_Wake up service/Alarm clock": 0.0,
 "Facility_Carpeted": 0.0,
 "Facility_Wake-up service": 0.0,
 "Facility_Alarm clock": 0.0,
 "Facility_Laptop safe": 0.0,
 "Facility_Upper floors accessible by elevator": 0.0,
 "Facility_Entire unit wheelchair accessible": 0.0,
 "Facility_Single-room air conditioning for guest accommodation": 0.0,
 "Ammendity_Swimming pool": 0.0,
 "Ammendity_Rooms/Facilities for Disabled": 0.0,
 "Ammendity_Spa & Wellness Centre": 0.0,
 "Facility_377 feet²": 0.0,
 "Facility_Streaming service (like Netflix)": 0.0,
 "Rating_Location": 0,
 "Facility_258 feet²": 0.0,
 "Facility_Bath": 0.0,
 "Facility_161 feet²": 0.0,
 "Facility_Hypoallergenic": 0.0,
 "Facility_Radio": 0.0,
 "Facility_Fold-up bed": 0.0,
 "Rating_Staff": 0,
 "Facility_344 feet²": 0.0,
 "Facility_Pay-per-view channels": 0.0,
 "Facility_Extra long beds (> 2 metres)": 0.0,
 "Facility_Detached": 0.0,
 "Facility_388 feet²": 0.0,
 "Facility_Lake view": 0.0,
 "Facility_Landmark view": 0.0,
 "Facility_River view": 0.0,
 "Facility_Barbecue": 0.0,
 "Facility_Sofa bed": 0.0,
 "Ammendity_Beach front": 0.0,
 "Facility_288 feet²": 0.0,
 "Facility_Heating": 0.0,
 "Facility_527 feet²": 0.0,
 "Facility_Coffee machine": 0.0,
 "Facility_Video": 0.0,
 "Facility_DVD player": 0.0,
 "Facility_CD player": 0.0,
 "Facility_Baby safety gates": 0.0,
 "Facility_334 feet²": 0.0,
 "Facility_Minibar": 0.0,
 "Facility_Bidet": 0.0,
 "Facility_Shared toilet": 0.0,
 "Facility_Shared bathroom": 0.0,
 "Facility_335 feet²": 0.0,
 "Facility_Patio": 0.0,
 "Facility_969 feet²": 0.0,
 "Facility_Pool view": 0.0,
 "Facility_Pool with a view": 0.0,
 "Facility_Additional bathroom": 0.0}
```

## Features
List of features ready and TODOs for future development
* get_available_listings_per_country
* get_available_listings_per_city

To-do list:

* <strike>get</strike>
* get_all_listings_per_country
* get_all_listings_per_city
* Upload package to pypi.org
* create swagger endpoints.
* Find available listings per multiple cities.
* Extend code to retrieve all room options, not just the cheapest room.
* Search hotel name.
* Change storage to mongodb (currently saved in csv).

## Status
Project is: _in progress_




