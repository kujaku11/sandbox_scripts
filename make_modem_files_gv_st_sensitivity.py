# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""


import os
from pathlib import Path
import numpy as np
import mtpy.modeling.modem as modem

# ==============================================================================
# Inputs
# ==============================================================================
dfn = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_sensitivity\st_1d_z03_t01_flat.dat")
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_sensitivity"
)

fn_stem = "st"
if not os.path.exists(save_path):
    os.mkdir(save_path)

# ==============================================================================
# Make the data file
# ==============================================================================
data_obj = modem.Data()
data_obj.read_data_file(dfn)

# ==============================================================================
# First make the mesh
# ==============================================================================
mod_obj = modem.Model(data_obj.station_locations)
mod_obj.cell_size_east = 750
mod_obj.cell_size_north = 750
mod_obj.pad_east = 7
mod_obj.pad_north = 7
mod_obj.pad_num = 4
mod_obj.ew_ext = 250000
mod_obj.ns_ext = 250000
mod_obj.z_mesh_method = "new"
mod_obj.z_bottom = 200000
mod_obj.z_target_depth = 70000
mod_obj.pad_z = 5
mod_obj.n_air_layers = 15
mod_obj.n_layers = 55
mod_obj.z1_layer = 30
mod_obj.pad_stretch_v = 1.8
mod_obj.res_initial_value = 50

# --> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()
mod_obj.plot_mesh()

mod_obj.write_model_file(save_path=save_path,
                        model_fn_basename="{0}_sm02.rho".format(fn_stem))

## =============================================================================
## Add topography
## =============================================================================
# mod_obj.add_topography_to_model2(topo_fn, airlayer_type="log_down")
# mod_obj.write_model_file(
#     save_path=save_path, model_fn_basename="{0}_sm02_topo.rho".format(fn_stem)
# )

# data_obj.center_stations(mod_obj.model_fn)
# a, b = data_obj.project_stations_on_topography(mod_obj)

# mod_obj.plot_mesh(fig_num=3)
# mod_obj.plot_topography()
# ==============================================================================
# make the covariance file
# ==============================================================================
cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.5
cov.smoothing_north = 0.5
cov.smoothing_z = 0.5
cov.smoothing_num = 1

cov.write_covariance_file(
    os.path.join(save_path, "covariance.cov"), model_fn=mod_obj.model_fn
)

# mod_obj.write_vtk_file(
#     vtk_save_path=save_path, vtk_fn_basename="{0}_sm_topo".format(fn_stem)
# )
# data_obj.write_vtk_station_file(
#     vtk_save_path=save_path, vtk_fn_basename="{0}_stations".format(fn_stem)
# )

mod_obj.print_mesh_params()
mod_obj.print_model_file_summary()

# cfg_obj = modem.ModEMConfig()
# cfg_obj.add_dict(obj=data_obj)
# cfg_obj.add_dict(obj=mod_obj)
# cfg_obj.add_dict(obj=cov)
# cfg_obj.write_config_file(save_dir=save_path,
#                          config_fn_basename='Inv01.cfg')
