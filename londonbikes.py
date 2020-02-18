#!/home/alrix/miniconda3/envs/jupyter/bin/python

import sys
from requests import request
import pandas as pd 
from pandas.io.json import json_normalize

usage = '''
Usage:
londonbikes search <search_string>
londonbikes search <latitude> <longitude> <radius_in_metres>
londonbikes id <bike_point_id>
'''

def query_search(query):
  url = "https://api.tfl.gov.uk/BikePoint/Search?query=" + query
  response=request(url=url, method='get').text

  # Put response into a dataframe
  df = pd.read_json(response)
  # Rename columns
  df.rename(columns={'id': 'Id', 'commonName': 'Name','lat':'Latitude','lon':'Longitude'}, inplace=True)
  # Return result
  print(df[['Id','Name','Latitude','Longitude']].to_string(index=False))

def geo_search(lat,lon,radius):
  url = "https://api.tfl.gov.uk/Place?includeChildren=false&type=BikePoint&placeGeo.lon=" + lon + "&placeGeo.lat=" + lat + '&radius=' + radius
  response=request(url=url, method='get')

  if response.status_code == 200 and len(response.json()['places']) > 0:
    # Put response into a dataframe
    df = json_normalize(response.json()['places'])
    # Concat lat and lon
    df['Latitude,Longitude'] = df['lat'].map(str) + ',' + df['lon'].map(str)
    # Rename columns
    df.rename(columns={'id': 'Id', 'commonName': 'Name', 'distance':'Distance'}, inplace=True)
    # Return result
    print(df[['Id','Name','Latitude,Longitude','Distance']].to_string(index=False))
  
  else:
    print("The search request is invalid")
    sys.exit(11)

def id_search(id):
  url = "https://api.tfl.gov.uk/BikePoint/" + id
  response=request(url=url, method='get')
  
  if response.status_code == 200:
    # Put response into dataframe
    df1 = json_normalize(response.json())
    df2 = json_normalize(response.json()['additionalProperties'])
    # Grab info
    df1['Num Bikes'] =  df2['value'].loc[df2['key'] == 'NbBikes'].to_string(index=False)
    df1['Empty Docks'] =  df2['value'].loc[df2['key'] == 'NbEmptyDocks'].to_string(index=False)
    #Format and return result
    df1.rename(columns={'commonName': 'Name','lat':'Latitude','lon':'Longitude'}, inplace=True)
    print(df1[['Name','Latitude','Longitude','Num Bikes','Empty Docks']].to_string(index=False))

  else:
    print("Bike point id", id ,"not recognized")
    sys.exit(13)

if len(sys.argv) > 1:
  command = str(sys.argv[1])

  if command == "id":
    if len(sys.argv) < 3 or len(sys.argv) > 3:
      print("Please specify a bike point id")
      sys.exit(12)
    else:
      id = str(sys.argv[2])
      id_search(id)
  elif command == "search":
    # Exit if length of search query is not 1 or 3
    if len(sys.argv) == 2 or len(sys.argv) == 4 or len(sys.argv) > 5:
      print("Please specify a search term")
      sys.exit(10)
    # if only single term called, use query_search
    elif len(sys.argv) == 3:
      query = str(sys.argv[2])
      query_search(query)
    # if 3 args called, use geo_search
    elif len(sys.argv) == 5:
      lat = str(sys.argv[2])
      lon = str(sys.argv[3])
      rad = str(sys.argv[4])
      geo_search(lat,lon,rad)
  else:
    print(usage)
    sys.exit(1)
      
else:
  print(usage)
  sys.exit(1)
