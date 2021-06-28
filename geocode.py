from numpy import NaN, add
import pandas as pd
from pandas.core.dtypes.missing import notnull
from pandas.core.indexes import base
import requests
import os
import gmplot

# ********************************************* Constants **********************************************
# Google API Key used for Maps API - Can use different key here if you have one
API_KEY = os.environ.get('MAPS_API_KEY')
#API_KEY = 'put own key here'
# Name of output file and its path
OUTPUT_FILE = 'outputData.csv'
# Name of input file and its path, '.' is the current working directory
INPUT_FILE = "./data-raw-short.csv"

# Only use the below constants to hardcode the location / coordinates
#CENTER_MAP_LOCATION = 'Seattle WA'
#CENTER_MAP_LAT = '47.608013'
#CENTER_MAP_LON = '-122.335167'
OUTPUT_MAP = '.\map.html'

# ********************************************* Column Names *******************************************
# Edit the column names as needed to fit the data coming in to the program. These column names are the 
#                   column labels in the csv file that is INPUT_FILE
# Column name in INPUT_FILE that contains the full address
ADDRESS_COLUMN = ("ADDRESSSTREET")
# City
CITY_COLUMN = ("City Place")
# If no address, will have cross street to use
CROSS_STREET_COLUMN = ("CROSSSTREET")

# **************************************** Function Definitions ****************************************

# *********************************************** Geocode **********************************************
# Function to geocode addresses given to it and format them correctly. The complete_response_string
#                   argument is optional and is False by default.
# Preconditions:    The address being given to it is correct and able to be geocoded by Google's API. The
#                   The complete_response_string is a boolean value that is either left blank or 
#                   set to true. 
# Postconditions:   The function will return a dict to the calling function / object. It will include
#                   all of the information that was identified from the Google API.
# Notes:            N
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

# ********************************************* getAddresses *******************************************
# Function to take a dataframe object, parse the addresses out of it, and convert to a list of addressable
#                   locations that can be geocoded. This handles address locations as well as cross-street
#                   locations.        
# Preconditions:    df is a dataframe object with appropriate values in it. Column name constants are filled
#                   out correctly in the constants section at the top of the program. 
# Postconditions:   Will return a list of combined locations.
# Notes:            Uses pandas dataframe notnull to identify null column which signals what kind of location
#                   it is (address or cross-street)
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

# ******************************************** plotResults *********************************************
# Function to plot the locations/results that have been geocoded. Takes a parameter of results which is
#                   a list of dicts of geocoded locations.         
# Preconditions:    Results has geocoded location information populated in it. Everything is formatted
#                   correctly.
# Postconditions:   html map will be placed in current directory under name given as identified by the 
#                   constant value at the top of the program.
# Notes:            #200 feet = 60.96 meters / 100 feet = xx.xx meters / 60 feet = 18.28 meters
def plotResults(results, centerLat, centerLon):
    print('\nPlotting Results...\n')

    #center map and zoom level
    gmap = gmplot.GoogleMapPlotter(centerLat, centerLon, 10, apikey=API_KEY)

    for result in results:
        gmap.coloricon = "http://www.googlemapsmarkers.com/v1/%s/"
        lat = result['latitude']
        lon = result['longitude']
        gmap.marker(lat,lon,"blue", marker=False)

        #draw circle around marker, radius in meters       
        gmap.circle(lat, lon, 18.28)

    #where to draw map . = current directory
    gmap.draw(OUTPUT_MAP)


# *************************************** setMapCenterConstants ****************************************
# Function to set the coordinates of where the map will be centered as defined by user input. User will 
#                   input a city and state, which will be geocoded and return a result. The result will be
#                   parsed to get the latitude and longitude. The lat and lon will be returned to the calling
#                   function and the data will be stored in variables inside of main()               
# Preconditions:    The location parameter is a valid location that is able to be geocoded and will return
#                   an acceptable latitude and longitude
# Postconditions:   Returns the latitude and longitude to the calling function to store in variables
#                   
# Notes:            
def setMapCenterConstants(location):
    print('\nsetting map center constants...\n')
    result = geocode(location)
    lat = result['latitude']
    lon = result['longitude']
    return lat,lon


# ******************************************* Main Function ********************************************
def main():
    print('\nThis is Main...')
    # Read file and put into pandas dataframe
    df = pd.read_csv(INPUT_FILE)

    # Stop program and get user input location string
    CENTER_MAP_LOCATION = input("Enter location to center map (EX: Seattle WA) : ")

    # Attempt to geocode address given by user. If fail, go to except block.
    try:
        CENTER_MAP_LAT, CENTER_MAP_LON = setMapCenterConstants(CENTER_MAP_LOCATION)

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
        plotResults(geocodedResults, CENTER_MAP_LAT, CENTER_MAP_LON)

        # Write to csv
        pd.DataFrame(geocodedResults).to_csv(OUTPUT_FILE, encoding='utf8')
    
    # Could not geocode location
    except:
        print('Error - Bad Location to Center Map')

if __name__ == "__main__":
    main()