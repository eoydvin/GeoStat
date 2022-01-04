#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 17:01:51 2021

@author: erlend
"""
import requests
import pandas as pd

# Geometry specifications: 
# https://frost.met.no/concepts2.html#geometryspecification

# Get available stations in box:
# http://bboxfinder.com/#59.570506,10.517349,59.790616,10.962982
#from request_MET_FROST import get_available_gauges_in_area
#bbox = "POLYGON((10.55 59.57, 10.96 59.57, 11 59.80, 10.5 59.80, 10.55 59.50))"
#s = get_available_gauges_in_area(geometry=bbox)

#from request_MET_FROST import get_avaliable_precipitation_resolutions

#stations = ["SN17650", "SN17895", "SN19815", "SN17820", "SN17775", "SN17850",
#            "SN19820", "SN17870", "SN19810", "SN17875"]

#s = get_avaliable_precipitation_resolutions(stations[9])

def get_rain_from_frost_hourly(ids, start, end, elements="sum(precipitation_amount PT1H)", clientID="6e7d29f6-8f77-4317-b9a6-846a7052852c"):
    url = "https://frost.met.no/observations/v0.jsonld"
    reftime = f"{start}/{end}"
    headers = {"Accept": "application/json"}
    parameters = {
        "sources": ids,
        "referencetime": reftime,
        "elements": elements,
        "timeoffsets": "PT0H",
        "fields": "sourceId, referenceTime, value, elementId",
    }
    r = requests.get(url=url, params=parameters, headers=headers, auth=(clientID, ""))
    return r.json()

start = '2018-08-08T08:00:00' 
end = '2018-08-08T15:00:00'

met_stations = {   
    "FAGERSTRAND": {
        "shortname": "Fagerstrand",
        "id": "SN17775",
        "name": "FAGERSTRAND",
        "maxResolution": "PT1H", #"PT1M",
        "lat": "59.7377",
        "lon": "10.5886"
    },

    "Ås (NMBU)": {
        "shortname": "Ås (NMBU)",
        "id": "SN17850",
        "name": "ÅS",
        "maxResolution": "PT1H", #"PT10M",
        "lat": "59.6605",
        "lon": "10.7818"
    },
    
    "BLEKSLITJERN": {
        "shortname": "Blekslitjern",
        "id": "SN17780",
        "name": "BLEKSLITJERN",
        "maxResolution": "PT1H", #"PT10M",
        "lat": "59.8095",
        "lon": "10.6308"
    },
    "Rustadskogen": {
        "shortname": "Rustadskogen",
        "id": "SN17870",
        "name": "ÅS - RUSTADSKOGEN",
        "maxResolution": "PT1H", #"PT1M",
        "lat": "59.6703",
        "lon": "10.8107"
    },    
    "ASKIM - KYKKELSRUD": {
        "shortname": "Kykkelsrud",
        "id": "SN3720",
        "name": "ASKIM - KYKKELSRUD",
        "maxResolution": "PT1H", #"PT1M",
        "lat": "59.5873",
        "lon": "11.0962"
    },   
    
    "TOFTE - RULLETO": {
        "shortname": "Tofte",
        "id": "SN19825",
        "name": "TOFTE - RULLETO",
        "maxResolution": "PT1H", #"PT1M",
        "lat": "59.5513",
        "lon": "10.5813"
    },   
    "OSLO - BLINDERN": {
        "shortname": "Oslo (Blindern)",
        "id": "SN18700",
        "name": "OSLO - BLINDERN",
        "maxResolution": "PT1H", #"PT1M",
        "lat": "59.9423",
        "lon": "10.72"
    },  
}

#read stations to xarray, format used by Pycomlink
for i in met_stations:
    data = []
    time = []
    for j in get_rain_from_frost_hourly(met_stations[i]["id"], start, end)['data']:
        # read data to xarray
        data.append(j['observations'][0]['value'])
        time.append( j['referenceTime'] )
    df = pd.DataFrame(data={'time':time, 'PT1H':data})
    df = df.set_index('time')
    ds = df.to_xarray()
    ds.coords['latitude'] = met_stations[i]["lat"]
    ds.coords['longitude'] = met_stations[i]["lon"]
    ds.coords['maxResolution'] = met_stations[i]["maxResolution"]
    ds.coords['shortname'] = met_stations[i]["shortname"]
    ds.coords['id'] = met_stations[i]["id"]
    ds.coords['name'] = met_stations[i]["name"]
    ds.to_netcdf("./stations/"+ met_stations[i]["id"])







