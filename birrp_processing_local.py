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
coil_calibration_path = r"/mnt/hgfs/MTData/Ant_calibrations/rsp_cal"
birrp_path = r"/home/jpeacock/Documents/birrp/birrp52_4pcs16e9pts"
local_path = r"/mnt/hgfs/MTData/MSHS"
copy_edi_path = os.path.join(local_path, 'EDI_Files_birrp')
fn_copy = False
#==============================================================================
# Station to process and remote reference
#==============================================================================
station = 'ms86'
rr_station = 'ms12'
#rr_station = None

local_station_path = os.path.join(local_path, station)
if rr_station is not None:
    rr_local_station_path = os.path.join(local_path, rr_station)
else:
    rr_local_station_path = None
    
#==============================================================================
# Process data
#==============================================================================
b_param_dict = {'c2threshb':.45,
                'c2threshe':.45,
                'c2thresh1':.45,
                'ainuin':.9995,
                'ainlin':.0001,
                'nar':11}

kwargs_dict = {'calibration_list':['3154', '3164', '3264'],
               '_max_nread':16000000}


zp_obj = zp.Z3D_to_edi(station_dir=local_station_path,
                       rr_station_dir=rr_local_station_path)
zp_obj.birrp_exe = birrp_path
zp_obj.coil_cal_path = coil_calibration_path

plot_obj, comb_edi_fn = zp_obj.process_data(df_list=[4096, 256, 16],
                                            notch_dict={4096:{},
                                                        256:None,
                                                        16:None},
                                            max_blocks=3,
                                            sr_dict={4096:(1000., 25),
                                                     256:(24.999, .126), 
                                                     16:(.125, .0001)},
                                            birrp_param_dict=b_param_dict,
                                            **kwargs_dict)
                                            
cp_edi_fn = os.path.join(copy_edi_path, station+'.edi')
shutil.copy(comb_edi_fn, cp_edi_fn)
print '--> Copied {0} to {1}'.format(comb_edi_fn, cp_edi_fn)