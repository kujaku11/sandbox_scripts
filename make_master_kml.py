# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 16:43:30 2019

@author: jpeacock
"""

import os
import shutil

from mtpy.core import mt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import fiona

fiona.supported_drivers['KML'] = 'rw'

df_fn = pd.read_csv(r"c:\Users\jpeacock\all_edi_files_sorted.csv")
edi_dir = r"c:\Users\jpeacock\Documents\EDI_FILES"
datum = {'init':'epsg:4326'}

if not os.path.exists(edi_dir):
    os.mkdir(edi_dir)

mt_dict = dict([(key, []) for key in ['station', 'lat', 'lon', 'elev',
                                      'collected_by', 'date', 'min_period',
                                      'max_period', 'hx', 'hy', 'hz',
                                      'ex_length', 'ey_length', 'project', 
                                      'rating', 'n_comp']])
for fn in df_fn.fn_path:
    if not os.path.exists(os.path.join(edi_dir, os.path.basename(fn))):
        shutil.copy(fn, os.path.join(edi_dir, os.path.basename(fn)))
    mt_obj = mt.MT(fn)
    mt_dict['station'].append(mt_obj.station)
    mt_dict['lat'].append(mt_obj.lat)
    mt_dict['lon'].append(mt_obj.lon)
    mt_dict['elev'].append(mt_obj.elev)
    mt_dict['collected_by'].append(mt_obj.Site.acquired_by)
    try:
        mt_dict['date'].append(mt_obj.Site.start_date)
    except ValueError:
        print('Bad Start time: {0}'.format(fn))
        mt_dict['date'].append('Unknown')
    mt_dict['min_period'].append(1./mt_obj.Z.freq.max())
    mt_dict['max_period'].append(1./mt_obj.Z.freq.min())
    mt_dict['hx'].append(mt_obj.FieldNotes.Magnetometer_hx.acqchan)
    mt_dict['hy'].append(mt_obj.FieldNotes.Magnetometer_hy.acqchan)
    mt_dict['hz'].append(mt_obj.FieldNotes.Magnetometer_hz.acqchan)
    mt_dict['ex_length'].append(mt_obj.FieldNotes.Electrode_ex.get_length())
    mt_dict['ey_length'].append(mt_obj.FieldNotes.Electrode_ey.get_length())
    mt_dict['project'].append(mt_obj.Site.project)
    mt_dict['rating'].append(mt_obj.FieldNotes.DataQuality.rating)
    if mt_obj.Tipper.tipper.mean() == 0:
        mt_dict['n_comp'].append(4)
    else:
        mt_dict['n_comp'].append(5)
        

gdf = gpd.GeoDataFrame(mt_dict, crs=datum)
gdf['geometry'] = [Point(lon, lat) for lat, lon in zip(mt_dict['lat'], mt_dict['lon'])]

gdf.to_file(os.path.join(edi_dir, 'all_mt_stations.shp'))

# write kml file
#gdf = gdf.drop(['lat', 'lon'], axis=1)
gdf = gdf.rename(columns={'station':'name'})
gdf.to_file(os.path.join(edi_dir, 'all_mt_stations.kml'), driver='KML')