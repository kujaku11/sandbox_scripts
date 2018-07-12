# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 17:20:17 2016

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import os
import numpy as np

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\Rotated_W34N\Interpolated\Edited"
save_path = r"c:\Users\jpeacock\Documents\SaudiArabia\inversions\inv_03"
topo_fn = r"c:\Users\jpeacock\Documents\SaudiArabia\GIS\etopo1.asc"

fn_stem = 'sa'

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
inv_period_list = np.logspace(np.log10(0.003125),
                              np.log10(10922.),
                              num=23)
data_obj = modem.Data(edi_list=s_edi_list, 
                      period_list=inv_period_list)
data_obj.error_type_z = 'eigen_floor'
data_obj.error_value_z = 3.0
data_obj.error_type_tipper = 'abs_floor'
data_obj.error_value_tipper = 0.02
data_obj.inv_mode = '1'
data_obj.model_epsg = 32637
data_obj.get_mt_dict()
data_obj.fill_data_array()
data_obj.get_relative_station_locations()

s = data_obj.station_locations
s.rotate_stations(30)
data_obj.station_locations = s

data_obj.data_array['tip'][np.where(np.abs(data_obj.data_array['tip'] < .001))] = 0.0+1j*0.0
#--> here is where you can rotate the data
data_obj.write_data_file(save_path=save_path, 
                         fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat".format(
                                     fn_stem,    
                                     data_obj.error_value_z,
                                     100*data_obj.error_value_tipper),
                          fill=False)

#==============================================================================
# First make the mesh
#==============================================================================
mod_obj = modem.Model(stations_object=data_obj.station_locations)
#mod_obj.station_locations.rotate_stations(30)
mod_obj.cell_size_east = 2000.
mod_obj.cell_size_north = 2000.
mod_obj.pad_east = 12
mod_obj.pad_north = 12
mod_obj.pad_method = 'extent1'
mod_obj.z_mesh_method = 'original'
mod_obj.pad_stretch_h = 1.2
mod_obj.ew_ext = 300000.
mod_obj.ns_ext = 300000.
mod_obj.pad_z = 6
mod_obj.n_layers = 50
mod_obj.z1_layer = 10
mod_obj.z_target_depth = 90000.
mod_obj.z_bottom = 300000.

#--> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0.0

mod_obj.make_mesh()
mod_obj.plot_mesh(fig_num=2)

mod_obj.save_path = save_path
mod_obj.write_model_file(model_fn_basename='{0}_sm{1:02.0f}.rho'.format(fn_stem,
                         np.log10(mod_obj.res_initial_value)))

### =============================================================================
### Add topography
### =============================================================================
#mod_obj.data_obj = data_obj
#mod_obj.add_topography_to_mesh(topo_fn,
#                               max_elev=None,
#                               rotation_angle=30)
#mod_obj.plot_topograph()
#mod_obj.write_model_file(model_fn_basename=os.path.join(save_path,
#                                               r"{0}_modem_sm02_topo.rho".format(fn_stem)))
#
## change data file to have relative topography
#data_obj.change_data_elevation(mod_obj)
#data_obj.write_data_file(save_path=save_path, 
#                         fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}_topo.dat".format(
#                                     fn_stem,
#                                     data_obj.error_value_z,
#                                     100*data_obj.error_value_tipper),
#                         elevation=True,
#                         fill=False)
##==============================================================================
## make the covariance file
##==============================================================================
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
