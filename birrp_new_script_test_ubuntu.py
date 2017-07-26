# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 16:47:08 2017

@author: jpeacock
"""

import mtpy.processing.new_birrp as birrp
import mtpy.usgs.zen_processing as zp
import numpy as np

reload(birrp)
reload(zp)

#h = zp.Z3D_to_edi(r"/mnt/hgfs/MTData/Geysers/gz02/TS")
#h.df_list = [256]
#h.rr_station_dir = [r"/mnt/hgfs/MTData/Geysers/gz08/TS", 
#                    r"/mnt/hgfs/MTData/Geysers/gz06/TS"]
h = zp.Z3D_to_edi(r"/mnt/hgfs/MTData/Geysers/gz13")
h.df_list = [256]
h.max_blocks = 3
h.rr_station_dir = [r"/mnt/hgfs/MTData/Geysers/gz28", 
                    r"/mnt/hgfs/MTData/Geysers/gz14"]
h.coil_cal_path = r"/mnt/hgfs/MTData/Ant_calibrations/rsp_cal"
h.birrp_exe = r"/home/jpeacock/Documents/birrp_5.3.2/birrp532_large"
t = h.make_mtpy_ascii_files()
sd = h.get_schedules_fn_from_dir(use_blocks_dict={256:[0, 1, 2]})
sf_list = h.write_script_files(sd)
#h.process_data()

#s_test = birrp.ScriptFile(**{'deltat':-256, 'c2threshe':.45})

#block_01 = np.zeros(6, dtype=s_test._fn_dtype)
#
#for ii, cc in enumerate(['ex', 'ey', 'hx', 'hy']):
#    block_01[ii]['fn'] = r"/mnt/hgfs/MTData/Geysers/gz06/TS/mb06_20170620_230518_256.{0}".format(cc.upper())
#    block_01[ii]['comp'] = cc  
#    block_01[ii]['nread'] = 7291904
#    block_01[ii]['nskip'] = 1
#    if cc in ['hx', 'hy']:
#        block_01[ii]['calibration_fn'] = r"/mnt/hgfs/MTData/Ant_calibrations/rsp_cal/ant_2264.csv"
#
#for jj, cc in enumerate(['hx', 'hy'], ii+1):
#    block_01[jj]['fn'] = r"/mnt/hgfs/MTData/Geysers/gz08/TS/mb08_20170620_230518_256.{0}".format(cc.upper())
#    block_01[jj]['comp'] = cc  
#    block_01[jj]['nread'] = 7291904
#    block_01[jj]['nskip'] = 1
#    block_01[jj]['rr'] = True
#    block_01[jj]['rr_num'] = 1
#    block_01[jj]['calibration_fn'] = r"/mnt/hgfs/MTData/Ant_calibrations/rsp_cal/ant_2264.csv"
#
##for kk, cc in enumerate(['hx', 'hy'], jj+1):
##    block_01[kk]['fn'] = r"/mnt/hgfs/MTData/Geysers/gz02/TS/mb02_20170620_230518_256.{0}".format(cc.upper())
##    block_01[kk]['comp'] = cc  
##    block_01[kk]['nread'] = 7291904
##    block_01[kk]['nskip'] = 1
##    block_01[kk]['rr'] = True
##    block_01[kk]['rr_num'] = 2
##    block_01[kk]['calibration_fn'] = r"/mnt/hgfs/MTData/Ant_calibrations/rsp_cal/ant_2264.csv"

#s_test.fn_arr = np.array([block_01, block_01])
#s_test.fn_arr = np.array(np.array(sd[256]))
##s_test.ilev = 1
##s_test.nrr = 0
#s_test.write_script_file(script_fn=r"c:/Users/jpeacock/Documents/GitHub/sandbox/test.script")
##s_test.write_config_file(r"c:/Users/jpeacock/Documents/GitHub/sandbox/test_script.cfg")