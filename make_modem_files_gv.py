# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""


import os
import numpy as np
import mtpy.modeling.modem as modem

# ==============================================================================
# Inputs
# ==============================================================================
edi_path = r"d:\Peacock\MTData\GabbsValley\EDI_Files_birrp\Edited\Rotated_m13_deg"
save_path = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\modem_inv\inv_03"
topo_fn = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\gis\gv_topo_60m.txt"
fn_stem = "gv"
s_edi_list = [
    os.path.join(edi_path, ss) for ss in os.listdir(edi_path) if ss.endswith(".edi")
]

if not os.path.exists(save_path):
    os.mkdir(save_path)

# ==============================================================================
# Make the data file
# ==============================================================================
inv_period_list = np.logspace(-np.log10(500), np.log10(1023), num=23)
data_obj = modem.Data(edi_list=s_edi_list, period_list=inv_period_list)

data_obj.error_type_z = "eigen_floor"
data_obj.error_value_z = 3.0
data_obj.error_type_tipper = "abs_floor"
data_obj.error_value_tipper = 0.02
data_obj.inv_mode = "1"
data_obj.model_epsg = 32611

# --> here is where you can rotate the data
data_obj.write_data_file(
    save_path=save_path,
    fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat".format(
        fn_stem, data_obj.error_value_z, 100 * data_obj.error_value_tipper
    ),
)

# ==============================================================================
# First make the mesh
# ==============================================================================
mod_obj = modem.Model(data_obj.station_locations)
mod_obj.cell_size_east = 200
mod_obj.cell_size_north = 200
mod_obj.pad_east = 10
mod_obj.pad_north = 10
mod_obj.pad_num = 7
mod_obj.ew_ext = 200000
mod_obj.ns_ext = 200000
mod_obj.z_mesh_method = "new"
mod_obj.z_bottom = 200000
mod_obj.z_target_depth = 30000
mod_obj.pad_z = 4
# mod_obj.n_air_layers = 20
mod_obj.n_layers = 50
mod_obj.z1_layer = 10
mod_obj.pad_stretch_v = 2.0

# --> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()

mod_obj.write_model_file(
    save_path=save_path, model_fn_basename="{0}_sm02.rho".format(fn_stem)
)

## =============================================================================
## Add topography
## =============================================================================
# mod_obj.add_topography_to_model2(topo_fn, airlayer_type='log_increasing_down')
# mod_obj.write_model_file(model_fn_basename='{0}_sm02_topo.rho'.format(fn_stem))
#
# data_obj.center_stations(mod_obj.model_fn)
# data_obj.project_stations_on_topography(mod_obj)
#
# mod_obj.plot_mesh(fig_num=3)
# mod_obj.plot_topography()
# ==============================================================================
# make the covariance file
# ==============================================================================
cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.2
cov.smoothing_north = 0.2
cov.smoothing_z = 0.2
cov.smoothing_num = 2

cov.write_covariance_file(
    os.path.join(save_path, "covariance.cov"), model_fn=mod_obj.model_fn
)

# mod_obj.write_vtk_file(vtk_save_path=save_path,
#                       vtk_fn_basename='{0}_sm_topo'.format(fn_stem))
# data_obj.write_vtk_station_file(vtk_save_path=save_path,
#                                vtk_fn_basename='{0}_stations'.format(fn_stem))

mod_obj.print_mesh_params()
mod_obj.print_model_file_summary()

# cfg_obj = modem.ModEMConfig()
# cfg_obj.add_dict(obj=data_obj)
# cfg_obj.add_dict(obj=mod_obj)
# cfg_obj.add_dict(obj=cov)
# cfg_obj.write_config_file(save_dir=save_path,
#                          config_fn_basename='Inv01.cfg')
