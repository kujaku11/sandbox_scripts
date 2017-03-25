# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 15:27:16 2013

@author: jpeacock-pr
"""

import os
import numpy as np
import garmin
import simplekml as kml

#kml_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\ProposedMTSitesNoNames.kml"
#txt_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\ProposedMTSites.txt"
#nkml_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\ProposedMTSitesShortNames.kml"

#kml_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\MTProposedSitesJune2014.kml"
#txt_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\MB_ProposedSites_May2014.txt"
#nkml_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\MTProposedSitesMay2014ShortNames.kml"

kml_file = r"c:\Users\jpeacock\Documents\iMush\iMush_edited_edi_files_JRP\imush_all_stations_edited.kml"
#kml_file = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\WFZ_Hite_MT_Preliminary.kml"
txt_file = '{0}.txt'.format(kml_file[:-4])
nkml_file = '{0}_no_name.kml'.format(kml_file[:-4])
#==============================================================================
# read in information from kml file
#==============================================================================

with open(kml_file, 'r') as kfid:
    klines = kfid.readlines()

station_list = []
lat_list = []
lon_list = []


ii = 200
for kline in klines:
    if kline.find('coordinates') > 0:
        klist = kline.strip().split(',')
        try:
            lon_list.append(float(klist[0].split('>')[1]))
            lat_list.append(float(klist[1].split('<')[0]))
            station_list.append('um{0:03}'.format(ii))
            ii += 1
        except ValueError:
            pass
        
    
        
#==============================================================================
# write information to a text file for a garmin
#==============================================================================

#tfid = file(txt_file, 'w')
#
#header_line = ','.join(['{0}'.format('station'),
#                       '{0}'.format('latitude'),
#                       '{0}\n'.format('longitude')])
#tfid.write(header_line)
#for station,lat,lon in zip(station_list, lat_list, lon_list):
#    tfid.write(','.join(['{0}'.format(station),
#                         '{0:.6f}'.format(lat),
#                         '{0:.6f}\n'.format(lon)]))
#tfid.close()


#==============================================================================
# write a kml file 
#==============================================================================
nkml = kml.Kml()

for station,lat,lon in zip(station_list, lat_list, lon_list):
    pnt = nkml.newpoint(name='', coords=[(lon,lat)])
    pnt.style.labelstyle.color = kml.Color.white
    pnt.style.labelstyle.scale = .8
#    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/dir_60.png'
    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/road_shield3.png'
    pnt.style.iconstyle.scale = .8

nkml.save(nkml_file)