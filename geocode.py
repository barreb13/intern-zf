from numpy import NaN, add
import pandas as pd
from pandas.core.dtypes.missing import notnull
from pandas.core.indexes import base
import requests
import os
import gmplot

# ****************************************** Constants ******************************************
# Google API Key used for Maps API - Can use different key here if you have one
API_KEY = os.environ.get('MAPS_API_KEY')
#API_KEY = 'put own key here'
# Name of output file and its path
OUTPUT_FILE = 'testOutput.csv'
# Name of input file and its path, '.' is the current working directory
INPUT_FILE = "./data-raw.csv"
#INPUT_FILE = "./data-raw-excel.xlsx"

# ******************************** Column Names - Edit as needed ********************************
# Column name in INPUT_FILE that contains the full address
ADDRESS_COLUMN = ("ADDRESSSTREET")
# City
CITY_COLUMN = ("City Place")
# If no address, will have cross street to use
CROSS_STREET_COLUMN = ("CROSSSTREET")

# ************************************ Function Definitions **************************************
# Function to get results from google
def geocode(address, complete_response_string=False):
    print('Geocoding...')

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
    if complete_response_string:
        output['response'] = response

    return output

# Function to parse data and get addresses to put in list
# Returns list of addresses
def getAddresses():
    print('Getting Addresses...')


# Function to write to map
def plotResults(results):
    print('Plotting Results...')

    #center map and zoom level
    gmap = gmplot.GoogleMapPlotter(47.608013,-122.335167, 10, apikey=API_KEY)

    for result in results:
        print('this is a result in the result list!')
        gmap.coloricon = "http://www.googlemapsmarkers.com/v1/%s/"
        lat = result['latitude']
        lon = result['longitude']
        print(lat,lon)

        #draw circle around marker, radius in meters
        #200 feet = 60.96 meters
        gmap.circle(48.1013714, -122.2271894, 60.96)

    #where to draw map (. = current directory)
    gmap.draw(".\map.html")


# ************************************** Main Function ******************************************
def main():
    print('This is Main...')
    df = pd.read_csv(INPUT_FILE)
    #print(df)

    # Handle where address column is null, so cross street location
    bool_series1 = pd.notnull(df[CROSS_STREET_COLUMN])
    #print(df[bool_series])
    df_crossStreet = df[bool_series1].copy()
    #format for list --> 'address, city'
    crossStreetAddresses = (df_crossStreet[CROSS_STREET_COLUMN] + ',' + df_crossStreet[CITY_COLUMN]).tolist()

    #Handle where address column not null, so address location
    bool_series2 = pd.notnull(df[ADDRESS_COLUMN])
    df_addresses = df[bool_series2].copy()
    #format for list --> 'address, city'
    addresses = (df_addresses[ADDRESS_COLUMN] + ',' + df_addresses[CITY_COLUMN]).tolist()

    print('\n\n Combining Lists Now... \n\n')

    combinedLocations = crossStreetAddresses + addresses
    
    for location in combinedLocations:
        print(location)

    # List for storing results
    geocodedResults = []

    for location in combinedLocations:
        geocodedResults.append(geocode(location))

    # Plot all found locations to a map
    plotResults(geocodedResults)

    # Write to csv
    pd.DataFrame(geocodedResults).to_csv(OUTPUT_FILE, encoding='utf8')

if __name__ == "__main__":
    main()

