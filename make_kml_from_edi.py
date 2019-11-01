# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 10:40:47 2014

@author: jpeacock-pr
"""

import geopandas as gpd
from shapely.geometry import Point
import fiona
import mtpy.core.mt as mt
import glob

fiona.supported_drivers['kml'] = 'rw'
fiona.supported_drivers['KML'] = 'rw'
crs = {'init':'epsg:4326'}

edi_path = r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\*.edi"

edi_list = glob.glob(edi_path)
                    
geometry = []
stations = {'ID':[],
            'elev':[],
            'lat':[],
            'lon':[]}

for edi in edi_list:
    mt_obj = mt.MT(edi)
    geometry.append(Point(mt_obj.lon, mt_obj.lat))
    stations['ID'].append(mt_obj.station)
    stations['elev'].append(mt_obj.elev)
    stations['lat'].append(mt_obj.lat)
    stations['lon'].append(mt_obj.lon)
    
gdf = gpd.GeoDataFrame(stations, crs=crs, geometry=geometry)
gdf.to_file(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\mv_mt_stations_all.kml",
            driver='kml')
#kml_obj.save(os.path.join(edi_path, "SAGE_2019_mt_stations.kml"))
    
            
            
