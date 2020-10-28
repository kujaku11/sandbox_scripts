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
    entry['elevation'] = mt_obj.elev
    entry['latitude'] = mt_obj.lat
    entry['longitude'] = mt_obj.lon
    entry['station'] = mt_obj.station
    entry['survey'] = mt_obj.Site.survey
    entry['start'] = mt_obj.Site.start_date
    entry['end'] = mt_obj.Site.end_date
    stations.append(entry)
    
# edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\ShanesBugs\Tongario_Hill\repeat")

# for edi in edi_path.glob('*.edi'):
#     mt_obj = mt.MT(edi)
#     geometry.append(Point(mt_obj.lon, mt_obj.lat))
#     entry = {}
#     entry['ID'] = mt_obj.station
#     entry['elevation'] = mt_obj.elev
#     entry['latitude'] = mt_obj.lat
#     entry['longitude'] = mt_obj.lon
#     entry['station'] = mt_obj.station + '-R'
#     entry['survey'] = 'Repeat'
#     entry['start'] = mt_obj._edi_obj.Info.info_list[7].split(':', 1)[1].strip().replace(' - ', 'T').replace('/', '-')
#     entry['end'] = mt_obj._edi_obj.Info.info_list[8].split(':', 1)[1].strip().replace(' - ', 'T').replace('/', '-')
#     stations.append(entry)
    
gdf = gpd.GeoDataFrame(stations, crs=crs, geometry=geometry)
# gdf.to_file(kml_fn+'.kml',
#             driver='kml')
gdf.to_file(shp_fn)
    
            
            
