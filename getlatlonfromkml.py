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
txt_file = '{0}.txt'.format(kml_file[:-4])
#nkml_file = r"c:\Users\jpeacock\Documents\LV\LV_2016_stations_names.kml"
#==============================================================================
# read in information from kml file
#==============================================================================

with open(kml_file, 'r') as kfid:
    klines = kfid.readlines()

station_lst = []
lat_lst = []
lon_lst = []


ii = 0
for kline in klines:
    if kline.find('coordinates') > 0:
        klst = kline.strip().split(',')
        lon_lst.append(float(klst[0].split('>')[1]))
        lat_lst.append(float(klst[1].split('<')[0]))
        station_lst.append('msh{0:03}'.format(ii))
        ii += 1
        
    
        
#==============================================================================
# write information to a text file for a garmin
#==============================================================================

tfid = file(txt_file, 'w')

header_line = ','.join(['{0}'.format('station'),
                       '{0}'.format('latitude'),
                       '{0}\n'.format('longitude')])
tfid.write(header_line)
for station,lat,lon in zip(station_lst, lat_lst, lon_lst):
    tfid.write(','.join(['{0}'.format(station),
                         '{0:.6f}'.format(lat),
                         '{0:.6f}\n'.format(lon)]))
tfid.close()


#==============================================================================
# write a kml file 
#==============================================================================
#nkml = kml.Kml()
#
#for station,lat,lon in zip(station_lst, lat_lst, lon_lst):
#    nkml.newpoint(name=str(int(station[2:])), coords=[(lon,lat)])
#
#nkml.save(nkml_file)