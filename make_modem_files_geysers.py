# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""
#==============================================================================
# Imports
#==============================================================================
import os
import numpy as np
import mtpy.modeling.modem as modem

#==============================================================================
# Inputs
#==============================================================================
<<<<<<< HEAD
# path to edi files
edi_path = r"c:\Users\jpeacock\Documents\ClearLake\EDI_Files_birrp\Edited\DR"

# path to save the modem files to 
save_path = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv02_dr"

# make the save folder if it doesn't already exist
=======
edi_path = r"c:\Users\jpeacock\Documents\ClearLake\EDI_Files_birrp\Edited\SS"
save_path = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03"

fn_stem = 'geysers'
s_edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
              if ss.endswith('.edi')]
                  
s_edi_list.remove(os.path.join(edi_path, 'gz05.edi'))
#s_edi_list.remove(os.path.join(edi_path, 'gz31.edi'))
                  
>>>>>>> 2dbb49e0d3a3b750b9f6d3c196bd630554021b22
if not os.path.exists(save_path):
    os.mkdir(save_path)

# all modem files with start with this
fn_stem = 'geysers'

# make a list of edi files
s_edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
              if ss.endswith('.edi')]
#==============================================================================
# Make the data file
#==============================================================================
# make a list of periods to invert over that are spaced evenly in log space
# format is np.logspace(highest frequency, lowest period, number of periods)
inv_period_list = np.logspace(-np.log10(500), np.log10(1023), num=23)

# make the data object
data_obj = modem.Data(edi_list=s_edi_list,
                      period_list=inv_period_list)

# set the error type for Z and T
data_obj.error_type_z = 'eigen_floor'
<<<<<<< HEAD
data_obj.error_value_z = 7.0

data_obj.error_type_tipper = 'abs_floor'
data_obj.error_value_tipper = .03

# set inversion mode
data_obj.inv_mode = '1'
=======
data_obj.error_value_z = 3.0
data_obj.inv_mode = '2'
>>>>>>> 2dbb49e0d3a3b750b9f6d3c196bd630554021b22

#--> here is where you can rotate the data
data_obj.rotation_angle = 0

# write out the data file
data_obj.write_data_file(save_path=save_path, 
                         fn_basename="{2}_modem_data_err{0:02.0f}_tip{1:02.0f}.dat".format(data_obj.error_value_z,
                                        data_obj.error_value_tipper*100, fn_stem))

#==============================================================================
# First make the mesh
#==============================================================================
mod_obj = modem.Model(data_obj.station_locations)

# cell size inside the station area
mod_obj.cell_size_east = 200
mod_obj.cell_size_north = 200

# number of cell_size cells outside the station area.  This is to reduce the
# effect of changin cell sized outside the station area
mod_obj.pad_num = 3

# number of padding cells going from edge of station area to ns_ext or ew_ext
mod_obj.pad_east = 10
mod_obj.pad_north = 10

# extension of the model in E-W direction or N-S direction and depth
# should be large enough to reduce edge effects
mod_obj.ew_ext = 350000
mod_obj.ns_ext = 350000
mod_obj.z_bottom = 250000

# target depth of the model, roughly where you want the model resolution to be
# optimal, roughly the deepest skin depth
mod_obj.z_target_depth = 30000

# padding from target depth to z_bottom
mod_obj.pad_z = 4

# number of layers
mod_obj.n_layers = 30

# thickness of 1st layer.  If you are not using topography or the topography 
# in your area is minimal, this is usually around 5 or 10 meters.  If the 
# topography is severe in the model area then a larger number is necessary to 
# minimize the number of extra layers.
mod_obj.z1_layer = 30

#--> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()
mod_obj.plot_mesh()

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

#==============================================================================
# Write a config file to remember what the parameters are
#==============================================================================
cfg_obj = modem.ModEM_Config()
cfg_obj.add_dict(obj=data_obj)
cfg_obj.add_dict(obj=mod_obj)
cfg_obj.add_dict(obj=cov)
cfg_obj.write_config_file(save_dir=save_path, 
                          config_fn_basename='Inv02_dr.cfg')
                          


