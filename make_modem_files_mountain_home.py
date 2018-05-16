# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""


import os
import numpy as np
import mtpy.modeling.modem as modem

#==============================================================================
# Inputs
#==============================================================================
edi_path = r"c:\Users\jpeacock\Documents\Geothermal\MountainHome\MountainHome_EDI_Files\INV_EDI_FILES"
save_path = r"c:\Users\jpeacock\Documents\Geothermal\MountainHome\modem_inv\inv_01"

fn_stem = 'mh'
s_edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
              if ss.endswith('.edi') and 'MHB' not in ss and 
              ss[0:4] not in ['MHW3', 'MHW4', 'MHW5']]
                
if not os.path.exists(save_path):
    os.mkdir(save_path)

#==============================================================================
# Make the data file
#==============================================================================
inv_period_list = np.logspace(-np.log10(300), np.log10(1023), num=23)
data_obj = modem.Data(edi_list=s_edi_list,
                      period_list=inv_period_list)

data_obj.error_type_z = 'eigen_floor'
data_obj.error_value_z = 3.0
data_obj.error_type_tipper = 'abs_floor'
data_obj.error_value_tipper = .02
data_obj.inv_mode = '1'
data_obj.model_epsg = 32611

#--> here is where you can rotate the data
data_obj.write_data_file(save_path=save_path, 
                          fn_basename='{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat'.format(
                                          fn_stem, 
                                          data_obj.error_value_z,
                                          data_obj.error_value_tipper*100))

#==============================================================================
# First make the mesh
#==============================================================================
mod_obj = modem.Model(data_obj.station_locations)
mod_obj.cell_size_east = 150
mod_obj.cell_size_north = 150
mod_obj.pad_east = 12
mod_obj.pad_north = 12
mod_obj.ew_ext = 300000
mod_obj.ns_ext = 300000
mod_obj.z_bottom = 250000
mod_obj.z_target_depth = 30000
mod_obj.pad_z = 4
mod_obj.pad_num = 3
mod_obj.n_layers = 50
mod_obj.z1_layer = 10
mod_obj.z_mesh_method = 'original'

#--> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()
mod_obj.plot_mesh()

mod_obj.write_model_file(save_path=save_path, 
                         model_fn_basename="{0}_sm02.rho".format(fn_stem))

#==============================================================================
# make the covariance file
#==============================================================================
cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.smoothing_num = 1

cov.write_covariance_file(cov_fn=os.path.join(save_path, 'covariance.cov'),
                          model_fn=mod_obj.model_fn)

mod_obj.print_model_file_summary()

cfg_obj = modem.ModEMConfig()
cfg_obj.add_dict(obj=data_obj)
cfg_obj.add_dict(obj=mod_obj)
cfg_obj.add_dict(obj=cov)
cfg_obj.write_config_file(save_dir=save_path, 
                          config_fn_basename='Inv01.cfg')

                          


