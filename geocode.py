from numpy import NaN, add
import pandas as pd
from pandas.core.dtypes.missing import notnull
from pandas.core.indexes import base
import requests
import os
import gmplot

# ****************************************** Constants *******************************************
# Google API Key used for Maps API - Can use different key here if you have one
API_KEY = os.environ.get('MAPS_API_KEY')
#API_KEY = 'put own key here'
# Name of output file and its path
OUTPUT_FILE = 'testOutput.csv'
# Name of input file and its path, '.' is the current working directory
INPUT_FILE = "./data-raw.csv"
CENTER_MAP_LAT = '47.608013'
CENTER_MAP_LON = '-122.335167'

# ****************************************** Column Names *****************************************
# Edit the column names as needed to fit the data coming in to the program.
# Column name in INPUT_FILE that contains the full address
ADDRESS_COLUMN = ("ADDRESSSTREET")
# City
CITY_COLUMN = ("City Place")
# If no address, will have cross street to use
CROSS_STREET_COLUMN = ("CROSSSTREET")

# ************************************* Function Definitions ****************************************

# ******************************************** Geocode **********************************************
# Function to geocode addresses given to it and format them correctly. The complete_response_string
#                   argument is optional and is False by default.
# Preconditions:    The address being given to it is correct and able to be geocoded by Google's API. The
#                   The complete_response_string is a boolean value that is either left blank or 
#                   set to true. 
# Postconditions:   The function will return a dict to the calling function / object. It will include
#                   all of the information that was identified from the Google API.
# Notes:            N
def geocode(address, complete_response_string=False):
    print('\nGeocoding...\n\n')

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
    # Conditional if user wants complete string, then add. Otherwise do not add
    if complete_response_string:
        output['response'] = response

    return output

# ****************************************** getAddresses **********************************************
# Currently getAddress loop is running in main() --> may move function in here         
# Preconditions:    R
# Postconditions:   T
# Notes:            N
def getAddresses(df):
    print('\nGetting Addresses...\n\n')
    # Handle where address column is null, so cross street location
    bool_series1 = pd.notnull(df[CROSS_STREET_COLUMN])
    df_crossStreet = df[bool_series1].copy()
    #format for list --> 'address, city'
    crossStreetAddresses = (df_crossStreet[CROSS_STREET_COLUMN] + ',' + df_crossStreet[CITY_COLUMN]).tolist()

    #Handle where address column not null, so address location
    bool_series2 = pd.notnull(df[ADDRESS_COLUMN])
    df_addresses = df[bool_series2].copy()
    #format for list --> 'address, city'
    addresses = (df_addresses[ADDRESS_COLUMN] + ',' + df_addresses[CITY_COLUMN]).tolist()

    #Combine lists of address locations and cross street locations
    combinedLocations = crossStreetAddresses + addresses

    return combinedLocations

# ******************************************** plotResults **********************************************
# Function to plot the locations/results that have been geocoded. Takes a parameter of results which is
#                   a list of dicts of geocoded locations.         
# Preconditions:    Results has geocoded location information populated in it. Everything is formatted
#                   correctly.
# Postconditions:   T
# Notes:            #200 feet = 60.96 meters / 100 feet = xx.xx meters / 60 feet = 18.28 meters
def plotResults(results):
    print('\nPlotting Results...\n\n')

    #center map and zoom level
    gmap = gmplot.GoogleMapPlotter(CENTER_MAP_LAT, CENTER_MAP_LON, 10, apikey=API_KEY)
    for result in results:
        gmap.coloricon = "http://www.googlemapsmarkers.com/v1/%s/"
        lat = result['latitude']
        lon = result['longitude']
        gmap.marker(lat,lon,"blue", marker=False)

        #draw circle around marker, radius in meters       
        gmap.circle(lat, lon, 18.28)

    #where to draw map . = current directory
    gmap.draw(".\map.html")


# ************************************** Main Function ******************************************
def main():
    print('This is Main...')
    df = pd.read_csv(INPUT_FILE)

    # Call getAddresses to extract address and store in combinedLocations
    combinedLocations = getAddresses(df)
    
    # Using for testing - take out if don't want/need to see each location
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