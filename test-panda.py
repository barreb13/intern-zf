import pandas as pd

#definitions
address_column_name = ("formatted_address")
input_file = "./test-data.csv"

#read the data and put in panda dataframe
data = pd.read_csv(input_file)

#print for testing
#print(data.columns)

#get all addresses from specific column and convert to list
addresses = data[address_column_name].tolist()

#for each address in the list, do something
for address in addresses:
    print(address)

