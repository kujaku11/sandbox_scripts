# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""


import os
from pathlib import Path
import numpy as np
import mtpy.modeling.modem as modem

#==============================================================================
# Inputs
#==============================================================================
edi_path = Path(r"c:\MT\GV2020\EDI_Files_birrp\Edited\GeographicNorth")
save_path = Path(r"c:\MT\GV2020\modem_inv\inv_01")
fn_stem = 'gv'
s_edi_list = list(edi_path.glob('*.edi'))

remove_list = ['gv04', 'gv14', 'gv21', 'gv03', 'gv10']
for ss in remove_list:
    s_edi_list.remove(edi_path.joinpath(ss + '.edi'))
                
if not os.path.exists(save_path):
    os.mkdir(save_path)

#==============================================================================
# Make the data file
#==============================================================================
inv_period_list = np.logspace(-np.log10(757), np.log10(2048), num=23)
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
                         fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat".format(
                                     fn_stem,    
                                     data_obj.error_value_z,
                                     100*data_obj.error_value_tipper))

#==============================================================================
# First make the mesh
#==============================================================================
mod_obj = modem.Model(data_obj.station_locations)
mod_obj.cell_size_east = 1000
mod_obj.cell_size_north = 1000
mod_obj.pad_east = 7
mod_obj.pad_north = 7
mod_obj.pad_num = 4
mod_obj.ew_ext = 200000
mod_obj.ns_ext = 200000
mod_obj.z_mesh_method = 'new'
mod_obj.z_bottom = 200000
mod_obj.z_target_depth = 70000
mod_obj.pad_z = 5
#mod_obj.n_air_layers = 20
mod_obj.n_layers = 60
mod_obj.z1_layer = 30
mod_obj.pad_stretch_v = 1.8

#--> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()
mod_obj.plot_mesh()

mod_obj.write_model_file(save_path=save_path, 
                         model_fn_basename="{0}_sm02.rho".format(fn_stem))

## =============================================================================
## Add topography
## =============================================================================
#mod_obj.add_topography_to_model2(topo_fn, airlayer_type='log_increasing_down')
#mod_obj.write_model_file(model_fn_basename='{0}_sm02_topo.rho'.format(fn_stem))
#
#data_obj.center_stations(mod_obj.model_fn)
#data_obj.project_stations_on_topography(mod_obj)
#
#mod_obj.plot_mesh(fig_num=3)
#mod_obj.plot_topography()
#==============================================================================
# make the covariance file
#==============================================================================
cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.smoothing_num = 1

cov.write_covariance_file(os.path.join(save_path, 'covariance.cov'),
                          model_fn=mod_obj.model_fn)

#mod_obj.write_vtk_file(vtk_save_path=save_path,
#                       vtk_fn_basename='{0}_sm_topo'.format(fn_stem))
#data_obj.write_vtk_station_file(vtk_save_path=save_path,
#                                vtk_fn_basename='{0}_stations'.format(fn_stem))

mod_obj.print_mesh_params()
mod_obj.print_model_file_summary()

#cfg_obj = modem.ModEMConfig()
#cfg_obj.add_dict(obj=data_obj)
#cfg_obj.add_dict(obj=mod_obj)
#cfg_obj.add_dict(obj=cov)
#cfg_obj.write_config_file(save_dir=save_path, 
#                          config_fn_basename='Inv01.cfg')
                          


