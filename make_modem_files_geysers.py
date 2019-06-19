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
edi_path = r"c:\Users\jpeacock\Documents\ClearLake\EDI_Files_birrp\Edited"
save_path = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv05"
topo_fn = r"c:\Users\jpeacock\Documents\ClearLake\dem\geysers_dem_150m.txt"

fn_stem = 'gz'
s_edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
              if ss.endswith('.edi')]
                  
if not os.path.exists(save_path):
    os.mkdir(save_path)
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
data_obj.error_value_z = 3.0

data_obj.error_type_tipper = 'abs_floor'
data_obj.error_value_tipper = .03

# set inversion mode
data_obj.inv_mode = '2'

# epsg code
data_obj.model_epsg = 32611

#--> here is where you can rotate the data
data_obj.rotation_angle = 0

# write out the data file
dfn = "{0}_modem_data".format(fn_stem)
if data_obj.rotation_angle != 0:
    if data_obj.rotation_angle < 0:
        dfn +='_rm{0:02.0f}'.format(data_obj.rotation_angle)
    else:
        dfn += '_r{0:02.0f}'.format(data_obj.rotation_angle) 

if data_obj.inv_mode == '2':
    dfn = "{0}_z{1:02.0f}.dat".format(dfn,
                                      data_obj.error_value_z)
    
elif data_obj.inv_mode == '5':
    dfn = "{0}_t{2:02.0f}.dat".format(dfn,
                                      data_obj.error_value_tipper*100)
else:
    dfn = "{0}_z{1:02.0f}_t{2:02.0f}.dat".format(dfn,
                                                 data_obj.error_value_z,
                                                 data_obj.error_value_tipper*100)
data_obj.write_data_file(save_path=save_path, 
                         fn_basename=dfn)


#==============================================================================
# First make the mesh
#==============================================================================
mod_obj = modem.Model(data_obj.station_locations)

# cell size inside the station area
mod_obj.cell_size_east = 200
mod_obj.cell_size_north = 200

### Padding information
mod_obj.pad_num = 8
mod_obj.pad_east = 10
mod_obj.pad_north = 10
mod_obj.pad_z = 5
mod_obj.pad_method = 'extent1'

# extension of the model in E-W direction or N-S direction and depth
# should be large enough to reduce edge effects
mod_obj.ew_ext = 350000
mod_obj.ns_ext = 350000
mod_obj.z_bottom = 250000
mod_obj.z_target_depth = 20000
mod_obj.pad_stretch_v = 2.5
mod_obj.res_initial_value = 50.0
mod_obj.z_mesh_method = 'new'

# number of layers
mod_obj.n_air_layers = 20
mod_obj.n_layers = 50

# thickness of 1st layer.  If you are not using topography or the topography 
# in your area is minimal, this is usually around 5 or 10 meters.  If the 
# topography is severe in the model area then a larger number is necessary to 
# minimize the number of extra layers.
mod_obj.z1_layer = 20

#--> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()

#--> add topography

mod_obj.add_topography_to_model2(topographyfile=topo_fn, 
                                 airlayer_type='log_increasing_down')

mod_obj.write_model_file(save_path=save_path,
                         model_fn_basename='{0}_sm02_topo.rho'.format(fn_stem))

### center stations
data_obj.center_stations(mod_obj.model_fn)
data_obj.project_stations_on_topography(mod_obj)

mod_obj.plot_mesh(fig_num=3)
mod_obj.plot_topography()
#==============================================================================
# make the covariance file
#==============================================================================
cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.5
cov.smoothing_north = 0.5
cov.smoothing_z = 0.5
cov.smoothing_num = 1

cov.write_covariance_file(os.path.join(save_path, 'covariance.cov'),
                          model_fn=mod_obj.model_fn)

# =============================================================================
# write vtk files
# =============================================================================
mod_obj.write_vtk_file(vtk_save_path=save_path,
                       vtk_fn_basename='{0}_sm_topo'.format(fn_stem))
data_obj.write_vtk_station_file(vtk_save_path=save_path,
                                vtk_fn_basename='{0}_stations'.format(fn_stem))

mod_obj.print_mesh_params()
###==============================================================================
### Write a config file to remember what the parameters are
###==============================================================================
##cfg_obj = modem.ModEMConfig()
##cfg_obj.add_dict(obj=data_obj)
##cfg_obj.add_dict(obj=mod_obj)
##cfg_obj.add_dict(obj=cov)
##cfg_obj.write_config_file(save_dir=save_path, 
##                          config_fn_basename='Inv04_rot.cfg')
      


