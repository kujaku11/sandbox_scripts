# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import os
import numpy as np

save_path = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_03"
edi_path = r"c:\Users\jpeacock\Documents\MountainPass\EDI_Files_birrp\Edited\geomag_north"
file_stem = 'mp'

s_edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
              if ss.endswith('.edi')]

# make mesh first


inv_period_list = np.logspace(-np.log10(625.), np.log10(1024.0), num=23)
data_obj = modem.Data(edi_list=s_edi_list,
                      period_list=inv_period_list)
data_obj.error_type_z = 'eigen_floor'
data_obj.error_value_z = 3.0
data_obj.inv_mode = '2'
data_obj.write_data_file(save_path=save_path, 
                         fn_basename="{0}_modem_data_ef{1:02.0f}.dat".format(file_stem, 
                                     data_obj.error_value_z))

mod_obj = modem.Model(station_object=data_obj.station_locations)
mod_obj.cell_size_east = 225
mod_obj.cell_size_north = 225
mod_obj.pad_east = 12
mod_obj.pad_north = 12
mod_obj.ew_ext = 200000
mod_obj.ns_ext = 200000
mod_obj.pad_method = 'extent1'
mod_obj.pad_stretch_h = 1.8
mod_obj.pad_z = 3
mod_obj.n_layers = 45
mod_obj.z_target_depth = 30000.


mod_obj.make_mesh()
mod_obj.plot_mesh()
mod_obj.save_path = save_path
mod_obj.write_model_file()

cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.smoothing_num = 2

cov.write_covariance_file(os.path.join(save_path, 'covariance.cov'))


