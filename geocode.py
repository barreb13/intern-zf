from numpy import NaN, add
import pandas as pd
from pandas.core.dtypes.missing import notnull
import requests
import os

# ****************************************** Constants ******************************************
# Google API Key used for Maps API - Can use different key here if you have one
API_KEY = os.environ.get('MAPS_API_KEY')
#API_KEY = os.environ.get('MAPS_API_KEY')
# Name of output file and its path
output_file = ''
# Name of input file and its path, '.' is the current working directory
input_file = "./data-raw.csv"

# ******************************** Column Names - Edit as needed ********************************
# Column name in input_file that contains the full address
address_column = ("ADDRESSSTREET")
# City
city_column = ("City Place")
# If no address, will have cross street to use
cross_street_column = ("CROSSSTREET")

# ************************************ Function Definitions **************************************
# Function to get results from google
def geocode(address):
    print('Geocoding...')

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
    return response

# Function to parse data and get addresses to put in list
# Returns list of addresses
def getAddresses():
    print('Getting Addresses...')


# Function to write to map
def plotResults():
    print('Plotting Results...')


# ************************************** Main Function ******************************************
def main():
    print('This is Main...')
    df = pd.read_csv(input_file)
    #print(df)

    # Handle where address column is null, so cross street location
    bool_series1 = pd.notnull(df[cross_street_column])
    #print(df[bool_series])
    df_crossStreet = df[bool_series1].copy()
    #format for list --> 'address, city'
    crossStreetAddresses = (df_crossStreet[cross_street_column] + ',' + df_crossStreet[city_column]).tolist()
    
    for address in crossStreetAddresses:
        print('cross streets' , address)

    #Handle where address column not null, so address location
    bool_series2 = pd.notnull(df[address_column])
    df_addresses = df[bool_series2].copy()
    #format for list --> 'address, city'
    addresses = (df_addresses[address_column] + ',' + df_addresses[city_column]).tolist()
    
    for address in addresses:
        print(address)

    print('\n\n Combining Lists Now... \n\n')

    combinedLocations = crossStreetAddresses + addresses
    for location in combinedLocations:
        print(location)

    # At this point all locations needing to be geocoded and mapped are in combinedLocations [] *****************************

    # List for storing results
    geocodedResults = []

    for location in combinedLocations:
        geocodedResults.append(geocode(location))



if __name__ == "__main__":
    main()

