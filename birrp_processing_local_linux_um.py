# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 12:32:29 2016

@author: jpeacock
"""

import os
import shutil
import mtpy.usgs.zen_processing as zp
# import pandas as pd
from pathlib import Path

#==============================================================================
# local parameters
#==============================================================================
coil_calibration_path = r"/mnt/hgfs/MT_Data/birrp_responses"
birrp_path = r"/home/peacock/Documents/birrp52/SourceCode/birrp52_big"
local_path = Path(r"/mnt/hgfs/MT_Data/UM2020")
copy_edi_path = local_path.joinpath('EDI_files_birrp')

if not copy_edi_path.exists():
    copy_edi_path.mkdir()

#==============================================================================
# Station to process and remote reference
#==============================================================================
station = 'um222'
# rr_station = ['gz214']
rr_station = None

block_dict = {4096: [0, 1, 2],
              256: [0, 1, 2],
              4: [0]}
use_df_list = [4096, 256, 4]
overwrite = False
df_overwrite = True
copy_edi = True

local_station_path = local_path.joinpath(station)
if rr_station is not None:
    if isinstance(rr_station, list):
        rr_local_station_path = []
        for rr in rr_station:
            rr_local_station_path.append(local_path.joinpath(rr))
    else:
        rr_local_station_path = local_path.joinpath(rr_station)
    ilev = 1
else:
    rr_local_station_path = None
    ilev = 0

dfn = local_station_path.joinpath('{0}_processing_df.csv'.format(station))
if not dfn.exists() or df_overwrite:
    dfn = None

#==============================================================================
# Process data
#==============================================================================
b_param_dict = {'ilev': ilev,
                'c2threshb': .35,
                'c2threshe': .35,
                'c2thresh1': .35,
                'ainuin': .9999,
                'ainlin': .0001,
                'nar': 9,
                'tbw': 2.5,
                'thetae': [0, 90, 0]}

zp_obj = zp.Z3D2EDI(station_z3d_dir=local_station_path,
                    rr_station_z3d_dir=rr_local_station_path) #,
                    # station_ts_dir=local_station_path.joinpath('TS'))
zp_obj.birrp_exe = birrp_path
zp_obj.calibration_path = coil_calibration_path
# zp_obj.survey_config_fn = Path(zp_obj.station_ts_dir).joinpath('{0}.cfg'.format(station))
# zp_obj.survey_config.read_survey_config_file(zp_obj.survey_config_fn,
#                                              station)
zp_obj._tol_dict[4]['s_diff'] = 6 * 4 * 3600
#zp_obj._tol_dict[256]['s_diff'] = .5 * 256 * 3600
kw_dict = {'df_fn': dfn,
           'df_list': use_df_list,
           'notch_dict': {4096: {}, 256: None, 4: None},
           'sr_dict': {4096: (1000., 25),
                       256: (24.49, .1),
                       4: (.1, .00001)},
           'use_blocks_dict': block_dict,
           'birrp_param_dict': b_param_dict,
           'overwrite': overwrite}

with zp.Capturing() as output:
    try:
        plot_obj, comb_edi_fn, zdf = zp_obj.process_data(**kw_dict)
        if copy_edi:
            cp_edi_fn = os.path.join(copy_edi_path, station+'.edi')
            shutil.copy(comb_edi_fn, cp_edi_fn)
            print('--> Copied {0} to {1}'.format(comb_edi_fn, cp_edi_fn))
        plot_obj.fig.savefig(os.path.join(copy_edi_path,
                                          '{0}.png'.format(station)),
                             dpi=300)

    except Exception as error:
        print('WARNING: Skipping {0}, rr = {1}'.format(station,
                                                       rr_station))
        print('x' * 50)
        print('ERROR: {0}'.format(error))
        print('x' * 50)

log_fn = local_path.joinpath('{0}_processing.log'.format(station))
with open(log_fn, 'a') as log_fid:
    log_fid.write('\n'.join(output))
    
print('\a' * 10)
