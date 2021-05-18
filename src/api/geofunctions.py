
import requests
import json
import time

ACCESS_KEY_TOKEN_LOCATIONIQ= 'pk.e8b1daa868f373b37187c866dc117043'
ACCESS_KEY_TOKEN_POSITIONSTACK = '7b7ccddaf4cfd0ed3c3038f792ba7ddc'




def get_locality_from_address(query):
    base_url = 'http://api.positionstack.com/v1/'
    while True:
        session = requests.Session()
        r = session.get(base_url+'forward?access_key={}&query={}'.format(ACCESS_KEY_TOKEN_POSITIONSTACK,query))
        data = r.json()
        try:
            localities = [data['data'][idx]['label'] for idx in range(len(data['data']))]
            if len(localities)>1:
                print('Ops, the location you have included, seems to appear in more than place.\nCleary you can only be at one place at any given time')
                print('Currrent results include:\n{}\nInclude country/town name to avoid multiple results.'.format(localities))
                return 'Multiple results'
            if len(localities)==0:
                print('No place found for {}'.format(query))
                return 'No place found'
            if len(localities)==1:
                response = data['data'][0]['administrative_area'] if data['data'][0]['administrative_area'] is not None else data['data'][0]['locality']
                return response
            break
        except TypeError:
            time.sleep(10)

def reverse_geocoding(lat,lng):
    # provider: https://locationiq.com/docs
    url = 'https://us1.locationiq.com/v1/reverse.php?key={}&lat={}&lon={}&format=json'.format(ACCESS_KEY_TOKEN_LOCATIONIQ,lat,lng)
    with requests.Session() as session:
        r = session.get(url).json()
        options = ['town','city']
        for option in options:
            try:
                city_name = (r['address'][option])
                return city_name
            except KeyError as ke:
                pass
