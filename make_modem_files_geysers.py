# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""
# ==============================================================================
# Imports
# ==============================================================================
from pathlib import Path
import numpy as np
import mtpy.modeling.modem as modem

# ==============================================================================
# Inputs
# ==============================================================================
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2022_EDI_files_birrp_processed\GeographicNorth\SS"
)
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2021"
)
topo_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\geysers_dem_150m.txt"
)
model_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\repeat_2022_01\gz_base_sm.rho"
)
dfn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\inv_2021_02\gz_modem_data_z03_tec.dat"
)

fn_stem = "gz"
model_epsg = 32610
# directives on what to do
write_data = False
write_model = True
write_cov = True
write_cfg = False
topography = True
center_stations = True
new_edis = False
old_center = False

if write_data and dfn.exists():
    dfn.unlink()

if not save_path.exists():
    save_path.mkdir()

# ==============================================================================
# Make the data file
# ==============================================================================
if write_data:
    s_edi_list = list(edi_path.glob("gz3*.edi"))
    # make a list of periods to invert over that are spaced evenly in log space
    # format is np.logspace(highest frequency, lowest period, number of periods)
    inv_period_list = np.logspace(-np.log10(500), np.log10(1023), num=23)

    # make the data object
    data_obj = modem.Data(edi_list=s_edi_list, period_list=inv_period_list)

    # set the error type for Z and T
    data_obj.error_type_z = "eigen_floor"
    data_obj.error_value_z = 5.0

    data_obj.error_type_tipper = "abs_floor"
    data_obj.error_value_tipper = 0.03

    # set inversion mode
    data_obj.inv_mode = "2"

    # epsg code
    data_obj.model_epsg = 32611

    # --> here is where you can rotate the data
    data_obj.rotation_angle = 0

    # write out the data file
    dfn = f"{fn_stem}_modem_data"
    if data_obj.rotation_angle != 0:
        if data_obj.rotation_angle < 0:
            dfn += f"_rm{data_obj.rotation_angle:02.0f}"
        else:
            dfn += f"_r{data_obj.rotation_angle:02.0f}"

    if data_obj.inv_mode == "2":
        dfn = f"{dfn}_z{data_obj.error_value_z:02.0f}.dat"

    elif data_obj.inv_mode == "5":
        dfn = f"{dfn}_t{data_obj.error_value_tipper * 100:02.0f}.dat"
    else:
        dfn = "{dfn}_z{data_obj.error_value_z:02.0f}_t{data_obj.error_value_tipper * 100:02.0f}.dat"
    data_obj.write_data_file(save_path=save_path, fn_basename=dfn)

else:
    data_obj = modem.Data()
    data_obj.read_data_file(dfn)
    data_obj.model_epsg = model_epsg

if old_center:
    data_obj._center_lat = 38.831979
    data_obj._center_lon = -122.828190
    data_obj.station_locations.calculate_rel_locations()


# ==============================================================================
# First make the mesh
# ==============================================================================
if write_model:
    mod_obj = modem.Model(data_obj.station_locations)

    # cell size inside the station area
    mod_obj.cell_size_east = 200
    mod_obj.cell_size_north = 200

    ### Padding information
    mod_obj.pad_num = 5
    mod_obj.pad_east = 10
    mod_obj.pad_north = 10
    mod_obj.pad_z = 5
    mod_obj.pad_method = "extent1"

    # extension of the model in E-W direction or N-S direction and depth
    # should be large enough to reduce edge effects
    mod_obj.ew_ext = 150000
    mod_obj.ns_ext = 150000
    mod_obj.z_bottom = 100000
    mod_obj.z_target_depth = 15000
    mod_obj.pad_stretch_v = 2.5
    mod_obj.res_initial_value = 50.0
    mod_obj.z_layer_rounding = 0
    mod_obj.z_mesh_method = "new"

    # number of layers
    mod_obj.n_air_layers = 40
    mod_obj.n_layers = 40

    # thickness of 1st layer.  If you are not using topography or the topography
    # in your area is minimal, this is usually around 5 or 10 meters.  If the
    # topography is severe in the model area then a larger number is necessary to
    # minimize the number of extra layers.
    mod_obj.z1_layer = 25

    # --> here is where you can rotate the mesh
    mod_obj.mesh_rotation_angle = 0

    mod_obj.make_mesh()

    # --> add topography
    if topography:
        mod_obj.add_topography_to_model2(
            topographyfile=topo_fn,
            airlayer_type="log_down",
            max_elev=1150,
        )

    mod_obj.write_model_file(
        save_path=save_path,
        model_fn_basename="{0}_sm02_topo.rho".format(fn_stem),
    )

else:
    mod_obj = modem.Model()
    mod_obj.read_model_file(model_fn)
    mod_obj.station_locations = data_obj.station_locations

### center stations and put on to the original grid.
if center_stations:
    data_obj.center_stations(mod_obj)
    mod_obj.station_locations = data_obj.station_locations

if topography:
    data_obj.project_stations_on_topography(mod_obj)
    mod_obj.station_locations = data_obj.station_locations

mod_obj.plot_mesh(fig_num=3)
mod_obj.print_mesh_params()
if topography:
    mod_obj.plot_topography()
# ==============================================================================
# make the covariance file
# ==============================================================================
cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.2
cov.smoothing_north = 0.2
cov.smoothing_z = 0.2
cov.smoothing_num = 2

cov.write_covariance_file(
    save_path.joinpath("covariance.cov"), model_fn=mod_obj.model_fn
)

# =============================================================================
# write vtk files
# =============================================================================
# mod_obj.write_vtk_file(
#     vtk_save_path=save_path, vtk_fn_basename="{0}_sm_topo".format(fn_stem)
# )
# data_obj.write_vtk_station_file(
#     vtk_save_path=save_path, vtk_fn_basename="{0}_stations".format(fn_stem)
# )

# mod_obj.print_mesh_params()
###==============================================================================
### Write a config file to remember what the parameters are
###==============================================================================
##cfg_obj = modem.ModEMConfig()
##cfg_obj.add_dict(obj=data_obj)
##cfg_obj.add_dict(obj=mod_obj)
##cfg_obj.add_dict(obj=cov)
##cfg_obj.write_config_file(save_dir=save_path,
##                          config_fn_basename='Inv04_rot.cfg')
