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
save_path = r"c:\Users\jpeacock\Documents\MountainPass\MusicValley\modem_inv\inv_03"
edi_path = r"d:\Peacock\MTData\MusicValley\EDI_Files_birrp\Edited\Rotated_m12_deg"
topo_fn = r"c:\Users\jpeacock\Documents\MountainPass\MusicValley\GIS\mv_dem_coarse.asc"

fn_stem = 'mp'

if not os.path.exists(save_path):
    os.mkdir(save_path)
# =============================================================================
# Get edi files
# =============================================================================
s_edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
              if ss.endswith('.edi')]
    
#==============================================================================
# Make the data file
#==============================================================================
inv_period_list = np.logspace(-np.log10(625.), np.log10(1024), num=23)
data_obj = modem.Data(edi_list=s_edi_list, 
                      period_list=inv_period_list)
data_obj.error_type_z = 'eigen_floor'
data_obj.error_value_z = 3.0
data_obj.error_type_tipper = 'abs'
data_obj.error_value_tipper = .02
data_obj.inv_mode = '1'
data_obj.model_epsg = 32611

#--> here is where you can rotate the data
data_obj.write_data_file(save_path=save_path, 
                         fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat".format(
                                     fn_stem,    
                                     data_obj.error_value_z,
                                     100*data_obj.error_value_tipper))

#==============================================================================
# First make the mesh
#==============================================================================
mod_obj = modem.Model(stations_object=data_obj.station_locations)
mod_obj.cell_size_east = 400
mod_obj.cell_size_north = 400
mod_obj.pad_east = 9
mod_obj.pad_north = 9
mod_obj.pad_method = 'extent1'
mod_obj.z_mesh_method = 'original'
mod_obj.pad_stretch_h = 1.7
mod_obj.pad_z = 5
mod_obj.n_layers = 40
mod_obj.z1_layer = 20
mod_obj.z_target_depth = 40000.
mod_obj.z_bottom = 180000.
mod_obj.n_air_layers = 20

#--> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()

mod_obj.save_path = save_path
mod_obj.write_model_file()

# =============================================================================
# Add topography
# =============================================================================
mod_obj.add_topography_to_model2(topo_fn, airlayer_type='log')
mod_obj.write_model_file(model_fn_basename='{0}_sm02_topo.rho'.format(fn_stem))

mod_obj.plot_mesh(fig_num=3)
mod_obj.plot_topography()

data_obj.project_stations_on_topography(mod_obj)

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

mod_obj.write_vtk_file(vtk_save_path=save_path,
                       vtk_fn_basename='{0}_sm_topo'.format(fn_stem))
data_obj.write_vtk_station_file(vtk_save_path=save_path,
                                vtk_fn_basename='{0}_stations'.format(fn_stem))

mod_obj.print_mesh_params()
