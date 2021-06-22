import pandas as pd
import requests
import os

# API key is stored in environment variable - Can use different one but need to manually type below
API_KEY = os.environ.get('MAPS_API_KEY')
address = '2nd,Custer, spokane'

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
print(response)

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

output['response'] = response

print(output)


# def get_google_results(address, api):
#     print("getting google results")
