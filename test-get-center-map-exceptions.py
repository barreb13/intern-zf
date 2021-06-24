import os
import requests

API_KEY = os.environ.get('MAPS_API_KEY')

def geocode(address, complete_response_string=False):
    print('\nGeocoding...\n')

    params = {
    'key': API_KEY,
    'address': address
    }

    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

    #creates request call and converts to json format
    #response = requests.get(base_url, params=params).json()
    results = requests.get(base_url, params=params)
    response = results.json()
    response.keys()

    if response['status'] == "OK":
        geometry = response['results'][0]['geometry']
        lat = geometry['location']['lat']
        lon = geometry['location']['lng']

    print(lat,lon)
    print(geometry)

    answer = response['results'][0]
    output = {
        "formatted_address" : answer.get('formatted_address'),
        "latitude": answer.get('geometry').get('location').get('lat'),
        "longitude": answer.get('geometry').get('location').get('lng'),
        "accuracy": answer.get('geometry').get('location_type'),
        "google_place_id": answer.get("place_id"),
        "type": ",".join(answer.get('types')),
        "postcode": ",".join([x['long_name'] for x in answer.get('address_components') 
                                if 'postal_code' in x.get('types')])
}

    output['input_string'] = address
    output['number_of_results'] = len(response['results'])
    output['status'] = response.get('status')
    # Conditional if user wants complete string, then add. Otherwise do not add
    if complete_response_string:
        output['response'] = response

    return output




CENTER_MAP_LOCATION = input("Enter location to center map (EX: Seattle, WA) : ")
print(CENTER_MAP_LOCATION)

try: 
    result = geocode(CENTER_MAP_LOCATION)
    print('successful')

except:
    print('bad')
