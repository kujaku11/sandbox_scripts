# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 15:27:16 2013

@author: jpeacock-pr
"""

import simplekml as kml
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import fiona

fiona.supported_drivers['KML'] = 'rw'
#kml_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\ProposedMTSitesNoNames.kml"
#txt_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\ProposedMTSites.txt"
#nkml_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\ProposedMTSitesShortNames.kml"

#kml_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\MTProposedSitesJune2014.kml"
#txt_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\MB_ProposedSites_May2014.txt"
#nkml_file = r"c:\Users\jpeacock-pr\Documents\MonoBasin\MTProposedSitesMay2014ShortNames.kml"

kml_file = r"c:\Users\jpeacock\Documents\kml_files\mnp_10km_propose_mt.kml"
#kml_file = r"c:\Users\jpeacock\Documents\Geothermal\Umatilla\WFZ_Hite_MT_Preliminary.kml"
txt_file = '{0}.txt'.format(kml_file[:-4])
csv_file = '{0}.csv'.format(kml_file[:-4])
shp_file = '{0}.shp'.format(kml_file[:-4])
nkml_file = '{0}_no_name.kml'.format(kml_file[:-4])
datum = {'init':'epsg:4326'}
#==============================================================================
# read in information from kml file
#==============================================================================

with open(kml_file, 'r') as kfid:
    klines = kfid.readlines()

df_dict = {'station':[], 'lat':[], 'lon':[]} 


ii = 100
for kline in klines:
    if kline.find('coordinates') > 0:
        klist = kline.strip().split(',')
        try:
            df_dict['lon'].append(float(klist[0].split('>')[1]))
            df_dict['lat'].append(float(klist[1].split('<')[0]))
            df_dict['station'].append('mnp{0:03}'.format(ii))
            ii += 1
        except ValueError:
            pass
        
df = pd.DataFrame(df_dict)

# write csv file
df.to_csv(csv_file, index=False)

# write shape file
gdf = gpd.GeoDataFrame(df, crs=datum, )
gdf['geometry'] = [Point(x[1]['lon'], x[1]['lat']) for x in df.iterrows()]
gdf.to_file(shp_file)

# write kml file
gdf = gdf.drop(['lat', 'lon'], axis=1)
gdf = gdf.rename(columns={'station':'name'})
gdf.to_file(nkml_file, driver='KML')
#==============================================================================
# write a kml file 
#==============================================================================
#nkml = kml.Kml()
#
#for station,lat,lon in zip(station_list, lat_list, lon_list):
#    pnt = nkml.newpoint(name='', coords=[(lon,lat)])
#    pnt.style.labelstyle.color = kml.Color.white
#    pnt.style.labelstyle.scale = .8
##    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/dir_60.png'
#    pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/road_shield3.png'
#    pnt.style.iconstyle.scale = .8
#
#nkml.save(nkml_file)