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
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Battle_Mountain\EDI_files_birrp\edited\GeographicNorth"
)
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Battle_Mountain\modem_inv\inv_03"
)
topo_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Battle_Mountain\GIS\bm_dem_wgs84_100m.asc"
)
fn_stem = "bm"
s_edi_list = list(edi_path.glob("*.edi"))

write_data = False
if not os.path.exists(save_path):
    os.mkdir(save_path)
# ==============================================================================
# Make the data file
# ==============================================================================
inv_period_list = np.logspace(-np.log10(757), np.log10(2048), num=23)

data_obj = modem.Data(edi_list=s_edi_list, period_list=inv_period_list)

data_obj.error_type_z = "eigen_floor"
data_obj.error_value_z = 3.0
data_obj.error_type_tipper = "abs_floor"
data_obj.error_value_tipper = 0.02
data_obj.inv_mode = "1"
data_obj.model_epsg = 32611

if write_data:

    # --> here is where you can rotate the data
    data_obj.write_data_file(
        save_path=save_path,
        fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat".format(
            fn_stem, data_obj.error_value_z, 100 * data_obj.error_value_tipper
        ),
    )

if write_data is False:
    data_obj.read_data_file(
        save_path.joinpath(
            f"{fn_stem}"
            f"_modem_data_z{data_obj.error_value_z:02.0f}"
            f"_t{100*data_obj.error_value_tipper:02.0f}.dat"
        )
    )


# ==============================================================================
# First make the mesh
# ==============================================================================
mod_obj = modem.Model(data_obj.station_locations)
mod_obj.cell_size_east = 400
mod_obj.cell_size_north = 400
mod_obj.pad_east = 15
mod_obj.pad_north = 15
mod_obj.pad_num = 4
mod_obj.ew_ext = 120000
mod_obj.ns_ext = 120000
mod_obj.z_mesh_method = "new"
mod_obj.z_bottom = 200000
mod_obj.z_target_depth = 20000
mod_obj.pad_z = 6
mod_obj.n_air_layers = 22
mod_obj.n_layers = 60
mod_obj.z1_layer = 20
mod_obj.pad_stretch_v = 1.8
mod_obj.z_layer_rounding = 1


# --> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()
# mod_obj.plot_mesh()

# mod_obj.write_model_file(save_path=save_path,
#                         model_fn_basename="{0}_sm02.rho".format(fn_stem))

## =============================================================================
## Add topography
## =============================================================================
mod_obj.add_topography_to_model2(
    topo_fn, airlayer_type="log_down", max_elev=1850
)
mod_obj.write_model_file(
    save_path=save_path, model_fn_basename="{0}_sm02_topo.rho".format(fn_stem)
)

data_obj.center_stations(mod_obj)
data_obj.project_stations_on_topography(mod_obj)

mod_obj.plot_mesh(fig_num=3)
mod_obj.plot_topography()
# ==============================================================================
# make the covariance file
# ==============================================================================
cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.smoothing_num = 1

cov.write_covariance_file(
    os.path.join(save_path, "covariance.cov"), model_fn=mod_obj.model_fn
)

mod_obj.write_vtk_file(
    vtk_save_path=save_path, vtk_fn_basename="{0}_sm_topo".format(fn_stem)
)
data_obj.write_vtk_station_file(
    vtk_save_path=save_path, vtk_fn_basename="{0}_stations".format(fn_stem)
)

mod_obj.print_mesh_params()
mod_obj.print_model_file_summary()

# cfg_obj = modem.ModEMConfig()
# cfg_obj.add_dict(obj=data_obj)
# cfg_obj.add_dict(obj=mod_obj)
# cfg_obj.add_dict(obj=cov)
# cfg_obj.write_config_file(save_dir=save_path,
#                          config_fn_basename='Inv01.cfg')
