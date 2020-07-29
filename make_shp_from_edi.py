# -*- coding: utf-8 -*-
"""
Created on Wed Dec 03 10:40:47 2014

@author: jpeacock-pr
"""

import geopandas as gpd
from shapely.geometry import Point
import fiona
import mtpy.core.mt as mt
from pathlib import Path

fiona.supported_drivers['kml'] = 'rw'
fiona.supported_drivers['KML'] = 'rw'
crs = {'init':'epsg:4326'}

edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_Files")
shp_fn = edi_path.joinpath('all_mt_stations.shp')
                    
geometry = []
stations = []

for edi in edi_path.glob('*.edi'):
    mt_obj = mt.MT(edi)
    geometry.append(Point(mt_obj.lon, mt_obj.lat))
    entry = {}
    entry['ID'] = mt_obj.station
    entry['elev'] = mt_obj.elev
    entry['lat'] = mt_obj.lat
    entry['lon'] = mt_obj.lon
    entry['station'] = mt_obj.station
    entry['acqby'] = mt_obj.Site.acquired_by
    entry['survey'] = mt_obj.Site.survey
    entry['date'] = mt_obj.Site.start_date
    stations.append(entry)
    
gdf = gpd.GeoDataFrame(stations, crs=crs, geometry=geometry)
# gdf.to_file(kml_fn+'.kml',
#             driver='kml')
gdf.to_file(shp_fn)
    
            
            
