# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 12:32:29 2016

@author: jpeacock
"""

import os
import shutil
import mtpy.usgs.zen_processing as zp

#==============================================================================
# local parameters
#==============================================================================
coil_calibration_path = r"/mnt/hgfs/MT/birrp_calibrations"
birrp_path = r"/home/peacock/Documents/birrp52/SourceCode/birrp52_big"
local_path = r"/mnt/hgfs/MT/MB"
copy_edi_path = os.path.join(local_path, 'EDI_Files_birrp')
processing_csv = r"/mng/hgfs/MT/MB/processing_loop.csv"

if not os.path.exists(copy_edi_path):
    os.mkdir(copy_edi_path)

#==============================================================================
# Station to process and remote reference
#==============================================================================
# loop_df = pd.read_csv(processing_csv)
# for loop in loop_df.itertuples()     
station = 'mb47'
rr_station = ['mb48', 'mb59']
# rr_station = None

# block_dict = {4096: [int(ss.strip() for ss in blocks_4096)],
#               256: [int(ss.strip() for ss in blocks_4096)],
#               4:[0]}

block_dict = {4096: [0, 1, 2],
              256: [1, 2, 3],
              4:[0]}

use_df_list = [4096, 256, 4]
overwrite = False

local_station_path = os.path.join(local_path, station)
if rr_station is not None:
    if isinstance(rr_station, list):
        rr_local_station_path = []
        for rr in rr_station:
            rr_local_station_path.append(os.path.join(local_path, rr))
    else:
        rr_local_station_path = os.path.join(local_path, rr_station)
    ilev=1
else:
    rr_local_station_path = None
    ilev = 0
    
#==============================================================================
# Process data
#==============================================================================

b_param_dict = {'ilev': ilev,
                'c2threshb': .45,
                'c2threshe': .45,
                'c2thresh1': .45,
                'ainuin': .9999,
                'ainlin': .0000,
                'nar': 7,
                'tbw': 2}

zp_obj = zp.Z3D2EDI(station_z3d_dir=local_station_path,
                    rr_station_z3d_dir=rr_local_station_path,
                    station_ts_dir=os.path.join(local_station_path, 'TS'))
zp_obj.birrp_exe = birrp_path
zp_obj.calibration_path = coil_calibration_path

plot_obj, comb_edi_fn, zdf = zp_obj.process_data(df_list=use_df_list,
                                                 notch_dict={4096:None,
                                                             256:None,
                                                             4:None},
                                                 sr_dict={4096:(1000., 25),
                                                          256:(24.999, .1), 
                                                          4:(.1, .00001)},
                                                 use_blocks_dict=block_dict,
                                                 birrp_param_dict=b_param_dict,
                                                 overwrite=overwrite)
                                            
cp_edi_fn = os.path.join(copy_edi_path, station+'.edi')
shutil.copy(comb_edi_fn, cp_edi_fn)
print('--> Copied {0} to {1}'.format(comb_edi_fn, cp_edi_fn))