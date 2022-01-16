#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 25 17:30:41 2021

@author: erlend
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 13:16:54 2021

@author: erlend
"""

import datetime
import numpy as np
import pandas as pd
from radar import radar_reflectivity_thredds
import pickle

lat_indice = [900, 1800] # 
lon_indice = [100, 700]

# eit program for å finne lat indice og lon indice baser på bbox

start = '2018-08-08' 
stop = '2018-08-08'
time_start = datetime.datetime.strptime(start, '%Y-%m-%d')
time_stop = datetime.datetime.strptime(stop, '%Y-%m-%d')
daterange = pd.date_range(time_start, time_stop).tolist()
# CML start = '2018-08-01' 
# CML end = '2018-09-11'


for date in daterange:
    ds = radar_reflectivity_thredds(date, lat_indice, lon_indice)
    
    #downloads a radar image for every 7,5 minute
    data = ds.variables['equivalent_reflectivity_factor'][:].data
    
    data[data == 9.96921e+36] = 0 # zero rainfall
    
    # map over norway
    map_norway_lon = ds.variables['lon'][:].data
    map_norway_lat = ds.variables['lat'][:].data
    
    reflectivity = {}
    reflectivity['lon'] = map_norway_lon
    reflectivity['lat'] = map_norway_lat
    for data_hour, time in zip(data, ds.variables['time'][:].data):
        reflectivity[datetime.datetime.fromtimestamp(time)] = [data_hour]

# too large for gitHub
a_file = open("/home/erlend/radar.pkl", "wb")
pickle.dump(reflectivity, a_file)
a_file.close()
        