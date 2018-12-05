# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 12:36:05 2018

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import os
import glob
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import mtpy.core.mt as mt

# =============================================================================
# Inputs
# =============================================================================
edi_dir = r"d:\Peacock\MTData\GraniteSprings\EDI_Files_birrp\Rotated_m13_deg\Edited"
save_dir = None
save_fn = r"gsv_mt_station_2018.shp"
datum = {'init':'epsg:4326'}

# =============================================================================
# make a shape file from edi files
# =============================================================================
edi_list = glob.glob(os.path.join(edi_dir, '*.edi'))

data_arr = np.zeros(len(edi_list), 
                    dtype=[('stationID', 'S12'),
                           ('latitude', np.float),
                           ('longitude', np.float),
                           ('elevation', np.float),
                           ('ex_len', np.float),
                           ('ey_len', np.float),
                           ('hx_sensor', 'S12'),
                           ('hy_sensor', 'S12'),
                           ('hz_sensor', 'S12'),
                           ('instrumentID', 'S12'),
                           ('start_date', 'S24'),
                           ('end_date', 'S24')])

for ii, edi in enumerate(edi_list):
    mt_obj = mt.MT(edi)
    data_arr['stationID'][ii] = mt_obj.station
    data_arr['latitude'][ii] = mt_obj.lat
    data_arr['longitude'][ii] = mt_obj.lon
    data_arr['ex_len'][ii] = mt_obj.FieldNotes.Electrode_ex.get_length()
    data_arr['ey_len'][ii] = mt_obj.FieldNotes.Electrode_ey.get_length()
    data_arr['hx_sensor'][ii] = mt_obj.FieldNotes.Magnetometer_hx.id
    data_arr['hy_sensor'][ii] = mt_obj.FieldNotes.Magnetometer_hy.id
    data_arr['hz_sensor'][ii] = mt_obj.FieldNotes.Magnetometer_hz.id
    data_arr['instrumentID'][ii] = mt_obj.FieldNotes.DataLogger.id
    data_arr['start_date'][ii] = mt_obj.Site.start_date
    data_arr['end_date'][ii] = mt_obj.Site.end_date

### make geopandas data frame with points    

gdf = gpd.GeoDataFrame(data_arr, crs=datum, )
gdf['geometry'] = [Point(x['longitude'], x['latitude']) for x in data_arr]

gdf.to_file(os.path.join(edi_dir, save_fn))


    