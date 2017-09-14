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
edi_path = r"c:\Users\jpeacock\Documents\ClearLake\EDI_Files_birrp\Edited\SS"
save_path = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03"

fn_stem = 'geysers'
s_edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
              if ss.endswith('.edi')]
                  
s_edi_list.remove(os.path.join(edi_path, 'gz05.edi'))
#s_edi_list.remove(os.path.join(edi_path, 'gz31.edi'))
                  
if not os.path.exists(save_path):
    os.mkdir(save_path)

#==============================================================================
# Make the data file
#==============================================================================
inv_period_list = np.logspace(-np.log10(500), np.log10(1023), num=23)
data_obj = modem.Data(edi_list=s_edi_list,
                      period_list=inv_period_list)

data_obj.error_type_z = 'eigen_floor'
data_obj.error_value_z = 3.0
data_obj.inv_mode = '2'

#--> here is where you can rotate the data
data_obj.write_data_file(save_path=save_path, 
                         fn_basename="{1}_modem_data_err{0:02.0f}.dat".format(data_obj.error_value_z,
                                        fn_stem))

#==============================================================================
# First make the mesh
#==============================================================================
mod_obj = modem.Model(data_obj.station_locations)
mod_obj.cell_size_east = 200
mod_obj.cell_size_north = 200
mod_obj.pad_east = 10
mod_obj.pad_north = 10
mod_obj.ew_ext = 350000
mod_obj.ns_ext = 350000
mod_obj.z_bottom = 250000
mod_obj.z_target_depth = 30000
mod_obj.pad_z = 4
mod_obj.pad_num = 3
mod_obj.n_layers = 30
mod_obj.z1_layer = 30

#--> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()
#mod_obj.plot_mesh()

mfn = os.path.join(save_path, r"{0}_modem_sm_02.rho".format(fn_stem))
mod_obj.write_model_file(**{'model_fn':mfn})
#==============================================================================
# make the covariance file
#==============================================================================
cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.3
cov.smoothing_north = 0.3
cov.smoothing_z = 0.3
cov.smoothing_num = 2

cov.write_covariance_file(os.path.join(save_path, 'covariance.cov'))

mod_obj.get_mesh_params()

cfg_obj = modem.ModEM_Config()
cfg_obj.add_dict(obj=data_obj)
cfg_obj.add_dict(obj=mod_obj)
cfg_obj.add_dict(obj=cov)
cfg_obj.write_config_file(save_dir=save_path, 
                          config_fn_basename='Inv02_dr.cfg')
                          


