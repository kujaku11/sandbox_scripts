#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 13:57:46 2020

@author: peacock
"""

from pathlib import Path
from mtpy.usgs import zen_processing as zp

station = 'mnp103'
rr_station = 'mnp104'
# rr_station = None
combine = False

#==============================================================================
# local parameters
#==============================================================================
coil_calibration_path = Path(r"/mnt/hgfs/MT/birrp_calibrations")
birrp_path = Path(r"/home/peacock/Documents/birrp52/SourceCode/birrp52_big")
local_path = Path(r"/mnt/hgfs/MT/MNP2019")
copy_edi_path = Path.joinpath(local_path, 'EDI_Files_birrp')
station_path = Path.joinpath(local_path, station)
survey_cfg_path = Path(r"/mnt/hgfs/MT/MNP2019/mnp103/TS/mnp103.cfg")
if rr_station is not None:
    rr_station_path = Path.joinpath(local_path, rr_station, 'TS')
    ilev = 1
else:
    rr_station_path = None
    ilev = 0


b_param_dict = {'ilev': ilev,
                'c2threshb':0,
                'c2threshe':.0,
                'c2thresh1':0,
                'ainuin':.9999,
                'ainlin':.0000,
                'nar':9}

# =============================================================================
# 
# =============================================================================

combine_fn_list = zp.combine_z3d_files(station_path)


zp_obj = zp.Z3D2EDI()
zp_obj.station_dir = (Path.joinpath(station_path, 'TS')).as_posix()
zp_obj.birrp_exe = birrp_path.as_posix()
zp_obj.coil_cal_path = coil_calibration_path.as_posix()
zp_obj.survey_config_fn = survey_cfg_path.as_posix()
zp_obj.survey_config.read_survey_config_file(survey_cfg_path.as_posix(), 
                                             station)
if rr_station is not None:
    zp_obj.rr_station_dir = rr_station_path.as_posix()

fn_arr = zp_obj.get_schedules_fn_from_dir(df_list=[4], 
                                          use_blocks_dict={4:'all'})

script_fn = zp_obj.write_script_files(fn_arr, birrp_params_dict=b_param_dict)
zp_obj.run_birrp(script_fn)

bf_path = Path.joinpath(Path(zp_obj.station_dir), 'BF', '4')
edi_fn = list(bf_path.glob('*.edi'))[-1]

rp = zp_obj.plot_responses([edi_fn])


