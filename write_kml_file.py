# -*- coding: utf-8 -*\-
"""
Created on Tue Jul 12 21:05:17 2016

@author: jpeacock-pr
"""

#import simplekml as skml
import mtpy.core.mt as mt
import os

edi_path = r"c:\MT\MB\zmmfiles"

#kml = skml.Kml()

edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi')]
                
for edi_fn in edi_list:
    mt_obj = mt.MT(edi_fn)
    print mt_obj.station, mt_obj.lat, mt_obj.lon
#    pnt = kml.newpoint(name=mt_obj.station, 
#                 coords=[(mt_obj.lon, mt_obj.lat)])
#    pnt.style.labelstyle.color = skml.Color.red  # Make the text red
#    pnt.style.labelstyle.scale = .8  # Make the text twice as big
#    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png'
#                 
#kml.save(os.path.join(edi_path, 'mon_lake_station_locations.kml'))