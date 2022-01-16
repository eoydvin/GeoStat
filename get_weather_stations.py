#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 17:01:51 2021

@author: erlend
"""
import requests
import pandas as pd
import pickle
import datetime

# get data from metadata
with open('/home/erlend/frost_id', 'r') as file:
    clientID = file.read().rstrip('\n')
    
def get_rain_from_frost_hourly(ids, start, end):
    elements="sum(precipitation_amount PT1H)", 
    url = "https://frost.met.no/observations/v0.jsonld"
    reftime = f"{start}/{end}"
    headers = {"Accept": "application/json"}
    parameters = {
        "sources": ids,
        "referencetime": reftime,
        "elements": elements,
    }
    r = requests.get(
        url=url, params=parameters, headers=headers, auth=(clientID, ""))
    return r.json()

#should be compatible with metadata file as not all stations are online always
#start = '2018-08-08T08:00:00' 
#end = '2018-08-08T15:00:00'
#start = '2018-08-07T08:00:00' 
#end = '2018-08-09T15:00:00'

start = '2018-06-07T08:00:00' 
end = '2019-09-09T15:00:00'

a_file = open("./stations/meta_data.pkl", "rb")
met_stations = pickle.load(a_file)

tot = len(met_stations)
c = 1
#read stations to xarray, format used by Pycomlink
for i in met_stations:
    data = []
    time = []
    
    r = get_rain_from_frost_hourly(met_stations[i]["id"], start, end)
    
    # not all stations are available as the "sources" API does not list the
    # start of indivitual measurements, rather the weather station as a whole
    
    if 'error' not in r:
        print('Added: ', i, ' (', c, '/', str(tot), ')')
        for j in r['data']:
            # read data to xarray
            data.append(j['observations'][0]['value'])
            time.append( datetime.datetime.strptime( 
                j['referenceTime'][0:19], '%Y-%m-%dT%H:%M:%S') )
            
        #read metadata
        df = pd.DataFrame(data={'time':time, 'PT1H':data})
        df = df.set_index('time')
        
        # convert to xarray labeled array
        ds = df.to_xarray()
        ds.coords['latitude'] = met_stations[i]["lat"]
        ds.coords['longitude'] = met_stations[i]["lon"]
        ds.coords['resolution'] = met_stations[i]["resolution"]
        ds.coords['shortname'] = met_stations[i]["shortname"]
        ds.coords['id'] = met_stations[i]["id"]
        ds.coords['name'] = met_stations[i]["name"]
        ds.to_netcdf("./stations/"+ met_stations[i]["id"])
    else:
        print('Skip: ', i, ' (', c, '/', str(tot), ')')

    c +=1

