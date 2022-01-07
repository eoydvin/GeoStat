#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 17:52:10 2021

@author: erlend
"""
import netCDF4

def radar_reflectivity_thredds(date, lat_indice, lon_indice):
    """
    Downloads radar image for given latitude and longitude indices. 
    """
    # lat and lon indices
    y = '[' + str(lat_indice[0]) + ':' + str(1) + ':' + str(lat_indice[1]) + ']' 
    x = '[' + str(lon_indice[0]) + ':' + str(1) + ':' + str(lon_indice[1]) + ']' 
    
    
    # 
    day = date.strftime('%d')
    month = date.strftime('%m')
    year = date.strftime('%Y')
    
    # dumb fixes in link as some days have missing values
    if year == '2018' and month == '08' and day == '07':
        time = '183'
        
    elif year == '2018' and month == '07' and (
            day == '03' or day == '04' or day == '13' or day == '14' or day == '18' or day == '21'):
        time = '190'    
    
    elif year == '2018' and month == '07' and (day == '15'):
        time = '188' 
        
    else: 
        time = '191'
        
    # Without lat lon cordinates
    #link = 'https://thredds.met.no/thredds/dodsC/remotesensing/reflectivity-nordic/'+ year + '/' + month +'/yrwms-nordic.mos.pcappi-0-dbz.noclass-clfilter-novpr-clcorr-block.laea-yrwms-1000.'+year+month+day+'.nc?time[0:1:'+time+'],equivalent_reflectivity_factor[0:1:' + time + ']' + y + x 
    
    # With lat lon coordinates. For verification
    link = 'https://thredds.met.no/thredds/dodsC/remotesensing/reflectivity-nordic/'+ year + '/' + month +'/yrwms-nordic.mos.pcappi-0-dbz.noclass-clfilter-novpr-clcorr-block.laea-yrwms-1000.'+year+month+day+'.nc?time[0:1:'+time+'],lon'+y + x+',lat'+ y + x +',equivalent_reflectivity_factor[0:1:' + time + ']' + y + x 
    ds=netCDF4.Dataset(link)

    return ds


def marshal_palmer(dBZ):
    return ( 10 **(dBZ/10) / 200)**(5/8)
    

# =============================================================================
# def get_xy_indices(min_lat, max_lat, min_lon, max_lon):
#     link = 'https://thredds.met.no/thredds/dodsC/remotesensing/reflectivity-nordic/2018/08/yrwms-nordic.mos.pcappi-0-dbz.noclass-clfilter-novpr-clcorr-block.laea-yrwms-1000.20180801.nc?Xc[0:1:2066],lon[0:2242][0:2066],lat[0:2242][0:2066]'
#     ds=netCDF4.Dataset(link)
# 
#     lat_bnds, lon_bnds = [min_lat, max_lat], [min_lon, max_lon]
#         
#     lats = ds.variables['lat'][:] 
#     lons = ds.variables['lon'][:]
#     
#     lat_bool = (lats > lat_bnds[0]) & (lats < lat_bnds[1])
#     lon_bool = (lons > lon_bnds[0]) & (lons < lon_bnds[1])
#         
#     lat_indice = [np.where(lat_bool != False)[0][0], np.where(lat_bool != False)[0][-1]]
#     lon_indice = [np.where(lon_bool != False)[1][0], np.where(lon_bool != False)[1][-1]]
#     
#     return lat_indice, lon_indice
# 
# =============================================================================