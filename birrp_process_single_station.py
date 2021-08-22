# -*- coding: utf-8 -*-
"""
Created on Thu Feb 02 13:50:01 2017

@author: jpeacock-pr
"""

import shutil
import os

#os.chdir(r"c:\Users\jpeacock-pr\Documents\GitHub\mtpy")
import mtpy.usgs.zen_processing as zp

survey_path = r"c:\MT\SCEC"
station = 'mvx031'
#rr_station = 'mvx008'
rr_station = None

bp = {'ilev':0,
      'nar':7,
      'ainuin':.9999,
      'ainlin':.0001,
      'c2threshb':.45,
      'thetab':[180, 90, 0],
      'thetae':[0, 90, 0]}
      
zp_obj = zp.Z3D_to_edi()
zp_obj.station_dir = os.path.join(survey_path, station)
if rr_station is not None:
    zp_obj.rr_station_dir = os.path.join(survey_path, rr_station)
else:
    zp_obj.rr_station_dir = None
zp_obj.coil_cal_path = r"c:\MT\Ant_calibrations"

#with zp.Capturing() as output:
n_dict_4096 = {'notches':[float(ii) for ii in range(60, 1860, 120)],
               'notch_radius':0.5,
               'freq_rad':0.5,
               'rp':0.1}
plot_obj, comb_edi = zp_obj.process_data(df_list=[4096, 256, 16],
                                         use_blocks_dict={4096:[0, 1, 2],
                                                          256:[1, 2],
                                                          16:[1, 2]},
                                         max_blocks=4,
                                         notch_dict={4096:n_dict_4096,
                                                     256:None, 
                                                     16:None}, 
                                         birrp_param_dict=bp,
                                         sr_dict={4096:(1000., 6.25),
                                                  256:(6.249, .016), 
                                                  16:(.0161, .0001)})
                                         
#
#plot_obj, comb_edi = zp_obj.process_data(df_list=[256],
#                                         use_blocks_dict={256:[0]},
#                                         max_blocks=1,
#                                         notch_dict={4096:{},
#                                                     256:None, 
#                                                     16:None},
#                                         birrp_param_dict=bp)
##                                         
#--> write log file
#    with open(os.path.join(zp_obj.station_dir, 'Processing.log'), 'w') as log_fid:
#        log_fid.write('\n'.join(output))
                                         
shutil.copy(comb_edi, 
            os.path.join(survey_path, 
                         'EDI_Files_birrp', '{0}.edi'.format(station)))

