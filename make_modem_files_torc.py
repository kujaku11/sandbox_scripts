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
edi_path = r"c:\Users\jpeacock\Documents\ShanesBugs\TorC_2018\EDIs_ga"
save_path = r"c:\Users\jpeacock\Documents\ShanesBugs\TorC_2018\modem_inv\inv_01"

if not os.path.exists(save_path):
    os.mkdir(save_path)
    
edi_list_fn = os.path.join(save_path, 'msh_shz_edi_files_big.pkl')

s_edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
              if ss.endswith('.edi')]
    



#==============================================================================
# Make the data file
#==============================================================================
inv_period_list = np.logspace(-np.log10(1000), np.log10(1024), num=23)
data_obj = modem.Data(edi_list=s_edi_list, 
                      period_list=inv_period_list)
data_obj.error_type_z = 'eigen_floor'
data_obj.error_type_tipper = 'absolute_floor'
data_obj.error_value_z = 3.0
data_obj.error_value_tipper = .02

#--> here is where you can rotate the data
data_obj.write_data_file(save_path=save_path, 
                         fn_basename="torc_modem_data_err{0:02.0f}_tip{1:02.0f}.dat".format(data_obj.error_value_z,
                                                        data_obj.error_value_tipper))


#==============================================================================
# First make the mesh
#==============================================================================
mod_obj = modem.Model(station_object=data_obj.station_locations)
mod_obj.cell_size_east = 250
mod_obj.cell_size_north = 250
mod_obj.pad_east = 8
mod_obj.pad_north = 8
mod_obj.pad_method = 'extent1'
mod_obj.z_mesh_method = 'original'
mod_obj.pad_stretch_h = 1.8
mod_obj.pad_z = 5
mod_obj.n_layers = 50
mod_obj.z1_layer = 10
mod_obj.z_target_depth = 40000.
mod_obj.z_bottom = 200000.

#--> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()
mod_obj.plot_mesh(fig_num=2)

mod_obj.save_path = save_path
mod_obj.write_model_file(model_fn=os.path.join(save_path, r"torc_modem_sm_02.rho"))

#==============================================================================
# make the covariance file
#==============================================================================
cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.smoothing_num = 1

cov.write_covariance_file(os.path.join(save_path, 'covariance.cov'))

mod_obj.print_mesh_params()
