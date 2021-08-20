from numpy import NaN, add
import pandas as pd
from pandas.core.dtypes.missing import notnull
from pandas.core.indexes import base
import requests
import os

# ********************************************* Constants **********************************************
# Google API Key used for Maps API - Can use different key here if you have one. This is stored
# in an environment variable for safety, but can also manually enter.
API_KEY = os.environ.get('MAPS_API_KEY')
#API_KEY = ''

# Name of input file and its path, '.' is the current working directory
#INPUT_FILE = './test.csv'
INPUT_FILE = r'C:\Users\Brent\Documents\UW Bothell\Capstone\csvFiles_to_geocode\county_okanogan_to_geocode.csv'

# Name of output file and its path
OUTPUT_FILE = r'C:\Users\Brent\Documents\UW Bothell\Capstone\csvFiles_geocoded\county_okanogan_geocoded.csv'


# ********************************************* Column Names *******************************************
# Edit the column names as needed to fit the data coming in to the program. These column names are the 
#                   column labels in the csv file that is INPUT_FILE
# Column name in INPUT_FILE that contains the full address
ADDRESS_COLUMN = ("address")
# City
CITY_COLUMN = ("township")
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
    print('\nGeocoding...')

    try:
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
    
    except:
        print('Error - Invalid Address')



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
    print('\nGetting Addresses...\n')
    # # Handle where address column is null, so cross street location
    # bool_series1 = pd.notnull(df[CROSS_STREET_COLUMN])
    # df_crossStreet = df[bool_series1].copy()
    # #format for list --> 'address, city'
    # crossStreetAddresses = (df_crossStreet[CROSS_STREET_COLUMN] + ',' + df_crossStreet[CITY_COLUMN]).tolist()

    #Handle where address column not null, so address location
    bool_series2 = pd.notnull(df[ADDRESS_COLUMN])
    df_addresses = df[bool_series2].copy()
    #format for list --> 'address, city'
    addresses = (df_addresses[ADDRESS_COLUMN] + ',' + df_addresses[CITY_COLUMN]).tolist()

    # #Combine lists of address locations and cross street locations
    # combinedLocations = crossStreetAddresses + addresses

    return addresses


# ******************************************* Main Function ********************************************
def main():
    # Read file and put into pandas dataframe
    df = pd.read_csv(INPUT_FILE)

    # Attempt to geocode address given by user. If fail, go to except block.
    try:
        # Call getAddresses to extract address and store in combinedLocations
        combinedLocations = getAddresses(df)

        # List for storing results
        geocodedResults = []

        for location in combinedLocations:
            result = geocode(location)
            #check for non-null value and append if valid
            if (result):
                geocodedResults.append(result)

        # Write to csv
        print('\nWriting to csv output file \n')
        pd.DataFrame(geocodedResults).to_csv(OUTPUT_FILE, encoding='utf8')

    # throw exception
    except:
        print('Something Went Wrong - Try Again')

if __name__ == "__main__":
    main()