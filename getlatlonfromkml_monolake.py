# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 15:27:16 2013

@author: jpeacock-pr
"""

#import os
#import numpy as np
#import garmin
import simplekml as kml

#kml_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\ProposedMTSitesNoNames.kml"
#txt_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\ProposedMTSites.txt"
#nkml_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\ProposedMTSitesShortNames.kml"

kml_file = r"c:\Users\jpeacock\Documents\MonoBasin\Mono_Lake_2015\MonoLake2017.kml"
txt_file = r"c:\Users\jpeacock\Documents\MonoBasin\Mono_Lake_2015\MonoLake2017.txt"
#nkml_file = r"C:\Users\jpeacock-pr\Google Drive\iMush\iMUSH_SiteStatus_2015_07_06_shortnames.kml"
#==============================================================================
# read in information from kml file
#==============================================================================
kfid = file(kml_file, 'r')

klines = kfid.readlines()

station_list = []
lat_list = []
lon_list = []

for ii, kline in enumerate(klines):
    if kline.find('coordinates') > 0:
        klist = kline.strip().split(',')
        if len(klist) > 1:
            lon_list.append(float(klist[0].split('>')[1]))
            lat_list.append(float(klist[1].split('<')[0]))
    if kline.find('name') > 0:
        station = kline.strip().split('>')[1].split('<')[0]
        if 'ml' in station and not station.endswith('.kml'):
            station_list.append(station)

        
#==============================================================================
# write information to a text file for a garmin
#==============================================================================

tfid = file(txt_file, 'w')

lines = [','.join(['{0}'.format('station'),
                   '{0}'.format('latitude'),
                   '{0}\n'.format('longitude')])]

for station,lat,lon in zip(station_list, lat_list, lon_list):
    lines.append(','.join(['{0}'.format(station),
                         '{0:.6f}'.format(lat),
                         '{0:.6f}\n'.format(lon)]))
with open(txt_file, 'w') as fid:
    fid.writelines(lines)


##==============================================================================
## write a kml file 
##==============================================================================
#nkml = kml.Kml()
#
#for station,lat,lon in zip(station_list, lat_list, lon_list):
#    nkml.newpoint(name=station, coords=[(lon,lat)])
#
#nkml.save(kml_file[0:-4]+'_num.kml')