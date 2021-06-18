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
response = requests.get(base_url, params=params).json()
response.keys()
print(response)

if response['status'] == "OK":
    geometry = response['results'][0]['geometry']
    lat = geometry['location']['lat']
    lon = geometry['location']['lng']

print(lat,lon)


# def get_google_results(address, api):
#     print("getting google results")
