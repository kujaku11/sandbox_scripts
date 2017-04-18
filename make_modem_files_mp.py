# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import os
import numpy as np

save_path = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_01"
edi_path = r"c:\Users\jpeacock\Documents\MountainPass\EDI_Files_birrp\Edited\geomag_north"
file_stem = 'mp'

s_edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
              if ss.endswith('.edi')]

# make mesh first
mod_obj = modem.Model(edi_list=s_edi_list)
mod_obj.cell_size_east = 400
mod_obj.cell_size_north = 400
mod_obj.pad_east = 15
mod_obj.pad_north = 15
mod_obj.pad_stretch_h = 1.6
mod_obj.pad_z = 5
mod_obj.n_layers = 50
mod_obj.z_target_depth = 40000.

mod_obj.make_mesh()
mod_obj.plot_mesh()

mod_obj.write_model_file(model_fn=os.path.join(save_path, 
                                               r"{0}_modem_sm.rho".format(file_stem)))

inv_period_list = np.logspace(-np.log10(625.), np.log10(1024.0), num=23)
data_obj = modem.Data(edi_list=s_edi_list, 
                      station_locations=mod_obj.station_locations,
                      period_list=inv_period_list)
data_obj.error_type = 'floor_egbert'
data_obj.error_egbert = 3.0
data_obj.inv_mode = '2'
data_obj.get_mt_dict()
data_obj._fill_data_array()
data_obj.data_array['elev'][:] = 0.0
data_obj.write_data_file(save_path=save_path, 
                         fn_basename="{0}_modem_data_ef{1:02.0f}.dat".format(file_stem, 
                                     data_obj.error_egbert))

cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.smoothing_num = 2

cov.write_covariance_file(os.path.join(save_path, 'covariance.cov'))


