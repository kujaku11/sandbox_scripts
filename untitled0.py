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
import mtpy.core.mt as mt


# =============================================================================
# Inputs
# =============================================================================
edi_dir = r"d:\Peacock\MTData\Camas\EDI_Files_birrp\Edited\Rotated_13_deg"
save_dir = None
save_fn = r"camas_mt_station_2018.shp"

# =============================================================================
# make a shape file from edi files
# =============================================================================
edi_list = glob.glob(os.path.join(edi_dir, '*.edi'))

data_array = np.zeros(len(edi_list), 
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
                             ('date_collected', np.datetime64)]

for edi in :
    mt_obj = mt.MT(edi)
    