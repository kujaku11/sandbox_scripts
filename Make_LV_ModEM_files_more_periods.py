# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 17:01:24 2014

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os
import numpy as np

#ps_path = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files_dp"
edi_path = r"/mnt/hgfs/Google Drive/Mono_Basin/INV_EDI_FILES"
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.find('.edi') > 0]
#--> remove any bad stations
bad_stations = [35, 110, 121, 132, 152]
for bad_station in bad_stations:
    edi_list.remove(os.path.join(edi_path, 'mb{0:03}.edi'.format(bad_station)))
                
#lv_path = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files"
#lv_list = edi_list = [os.path.join(lv_path, edi) for edi in os.listdir(lv_path)
#            if edi.find('.edi') > 0 and edi.find('LV') == 0]:
lv_bad_stations = [1, 11]
for lv_bad_station in lv_bad_stations:
    edi_list.remove(os.path.join(edi_path, 'LV{0:02}.edi'.format(lv_bad_station)))
#                
#edi_list = ps_list+lv_list
save_path = r"/home/jpeacock/Documents/ModEM/LV"

if os.path.isdir(save_path) is False:
    os.mkdir(save_path)

small_md = modem.Data()
small_md.read_data_file(r"/home/jpeacock/Documents/ModEM/LV/Layered1D_Inv1/LV_DP_egbert10.dat")


#--> make data file
md = modem.Data(edi_list=list(edi_list))
md.error_egbert = 7
md.error_tipper = .05
md.inv_mode = '1'
md.ptol = .15
md.period_list = [.003125, 
                  .0052083, 
                  .0125,
                  .025,
                  .05,
                  .08333,
                  .125,
                  .25,
                  .5,
                  .8,
                  1, 
                  2,
                  4,
                  8,
                  10.667,
                  12.8,
                  16,
                  32, 
                  64,
                  102.4,
                  128,
                  256,
                  516] 
md.station_locations = small_md.station_locations.copy()
    
#--> write data file
md.write_data_file(save_path=save_path, fn_basename='lv_dp_23p.dat')

data_fn = str(md.data_fn)

md = modem.Data()
md.read_data_file(data_fn)
md.error_egbert = 7
md.error_tipper = .05
# when removing points or adding error bars, need to do it in the mt_obj
## add error and remove bad data points from previously written data file
# remove bad Zyx in mb021
md.mt_dict['MB021'].Z.z[:, 1, :] = 0.0+0j

### add error to 106, 107, 109, 159 in Zyx
#for ss in [106, 107, 109, 159]:
#    index_ss = np.where(md.data_array['station'] == 'MB{0:03}'.format(ss))
#    md.data_array[index_ss]['z_err'][9:, 1, :] *= 20

## remove all tipper information for all wannamaker's stations
for lv_ss in range(25):
    try:
        md.mt_dict['LV{0:02}'.format(lv_ss)].Tipper.tipper[:, :, :] = 0+0j
    except KeyError:
        pass
    
md._fill_data_array()
    
md.write_data_file(save_path=save_path, fn_basename='lv_dp_23p.dat')    
md.inv_mode = '2'
md.write_data_file(save_path=save_path, fn_basename='lv_dp_23p_no_tipper.dat')
md.inv_mode = '5'
md.write_data_file(save_path=save_path, fn_basename='lv_dp_23p_tipper.dat')

##--> make control files
#cntrl_inv = modem.Control_Inv()
#cntrl_inv.write_control_file(save_path=save_path)
#
#cntrl_fwd = modem.Control_Fwd()
#cntrl_fwd.write_control_file(save_path=save_path)
#
##--> make covariance file
#cov = modem.Covariance()
#cov.grid_dimensions = (mesh.grid_north.shape[0], 
#                       mesh.grid_east.shape[0],
#                       mesh.grid_z.shape[0])
#cov.smoothing_east = 0.5
#cov.smoothing_north = 0.5
#cov.smoothing_z = 0.5
#cov.smoothing_num = 2
#cov.write_covariance_file(save_path=save_path)
                