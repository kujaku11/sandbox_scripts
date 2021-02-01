# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""
# ==============================================================================
# Imports
# ==============================================================================
import os
import numpy as np
from pathlib import Path
import mtpy.modeling.modem as modem
from mtpy.core import mt_collection

# ==============================================================================
# Inputs
# ==============================================================================
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_06\new_edis"
)
csv_fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\all_mt_stations_02.csv")
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\\Geothermal\Umatilla\modem_inv\inv_09"
)
topo_fn = (
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\dem\umatilla_dem_200m.txt"
)
fn_stem = "um"
dfn = save_path.joinpath("{0}_modem_data_z05_topo_edit.dat".format(fn_stem))

# Geothermal Zone
bounds = {"lat": np.array([45.25, 45.75]), "lon": np.array([-118.8, -118.3])}
# zone 00
# bounds = {"lat": np.array([45.65, 45.6833]),
#           "lon": np.array([-118.591666, -118.55])}

# 1D starting model (bottom depth, resistivity)
# sm_1d = [(0, 20, 10), (20, 500, 500), (500, 2000, 50)]
sm_1d = None

avg_radius = None
model_epsg = 32611
if not os.path.exists(save_path):
    os.mkdir(save_path)

write_data = False
write_model = True
write_cov = True
write_cfg = False
topography = True
center_stations = False
new_edis = True

if write_data and dfn.exists():
    os.remove(dfn)

if not save_path.exists():
    save_path.mkdir()
# ==============================================================================
# Make the data file
# ==============================================================================
if write_data:
    if bounds is not None:
        mc = mt_collection.MTCollection()
        mc.from_csv(csv_fn)
        bbox_df = mc.apply_bbox(
            bounds["lon"].min(),
            bounds["lon"].max(),
            bounds["lat"].min(),
            bounds["lat"].max(),
        )

        s_edi_list = bbox_df.fn.to_list()
    else:
        s_edi_list = list(edi_path.glob("*.edi"))
    # make a list of periods to invert over that are spaced evenly in log space
    # format is np.logspace(highest frequency, lowest period, number of periods)
    inv_period_list = np.logspace(-np.log10(700.1), np.log10(300), num=23)

    # make the data object
    data_obj = modem.Data(edi_list=s_edi_list, period_list=inv_period_list)

    # set the error type for Z and T
    data_obj.error_type_z = "eigen_floor"
    data_obj.error_value_z = 5.0

    data_obj.error_type_tipper = "abs_floor"
    data_obj.error_value_tipper = 0.03

    data_obj.model_epsg = model_epsg

    # set inversion mode
    data_obj.inv_mode = "2"

    # --> here is where you can rotate the data
    data_obj.rotation_angle = 0

    # write out the data file
    if data_obj.inv_mode == "2":
        data_obj.write_data_file(
            save_path=save_path,
            fn_basename="{0}_modem_data_z{1:02.0f}.dat".format(
                fn_stem, data_obj.error_value_z
            ),
            fill=True,
            compute_error=True,
            elevation=False,
            new_edis=new_edis,
        )
    elif data_obj.inv_mode == "5":
        data_obj.write_data_file(
            save_path=save_path,
            fn_basename="{0}_modem_data_t{1:02.0f}.dat".format(
                fn_stem, data_obj.error_value_tipper * 100
            ),
            fill=True,
            compute_error=True,
            elevation=False,
            new_edis=new_edis,
        )
    else:
        data_obj.write_data_file(
            save_path,
            fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat".format(
                fn_stem, data_obj.error_value_z, data_obj.error_value_tipper * 100
            ),
            fill=True,
            compute_error=True,
            elevation=False,
            new_edis=new_edis,
        )
else:
    data_obj = modem.Data()
    data_obj.read_data_file(dfn)
    data_obj.model_epsg = model_epsg
# ==============================================================================
# First make the mesh
# ==============================================================================
if write_model:
    mod_obj = modem.Model(data_obj.station_locations)

    # cell size inside the station area
    mod_obj.cell_size_east = 250
    mod_obj.cell_size_north = 250

    # number of cell_size cells outside the station area.  This is to reduce the
    # effect of changin cell sized outside the station area
    mod_obj.pad_num = 5

    # number of padding cells going from edge of station area to ns_ext or ew_ext
    mod_obj.pad_east = 8
    mod_obj.pad_north = 8

    # extension of the model in E-W direction or N-S direction and depth
    # should be large enough to reduce edge effects
    mod_obj.ew_ext = 150000
    mod_obj.ns_ext = 150000
    mod_obj.z_bottom = 100000
    mod_obj.pad_stretch_h = 1.13
    mod_obj.pad_stretch_v = 1.3

    # target depth of the model, roughly where you want the model resolution to be
    # optimal, roughly the deepest skin depth
    mod_obj.z_target_depth = 15000

    # padding from target depth to z_bottom
    mod_obj.pad_z = 8

    # number of layers
    mod_obj.n_layers = 35
    mod_obj.n_air_layers = 30

    # thickness of 1st layer.  If you are not using topography or the topography
    # in your area is minimal, this is usually around 5 or 10 meters.  If the
    # topography is severe in the model area then a larger number is necessary to
    # minimize the number of extra layers.
    mod_obj.z1_layer = 5
    mod_obj.z_layer_rounding = -1

    # --> here is where you can rotate the mesh
    mod_obj.mesh_rotation_angle = 0

    mod_obj.make_mesh()

    # new_north = (
    #     list(mod_obj.nodes_north[0:7])
    #     + [round(120 + 120 * 0.15 * ii) for ii in range(14)][::-1]
    #     + [100] * 38
    #     + [round(120 + 120 * 0.15 * ii) for ii in range(10)]
    #     + list(mod_obj.nodes_north[0:7])[::-1]
    # )

    # new_east = (
    #     list(mod_obj.nodes_east[0:7])
    #     + [round(120 + 120 * 0.15 * ii) for ii in range(20)][::-1]
    #     + [100] * 42
    #     + [round(120 + 120 * 0.16 * ii) for ii in range(15)]
    #     + [round(120 + 120 * 0.16 * ii) for ii in range(15)][::-1]
    #     + [100] * 5
    #     + [round(120 + 120 * 0.15 * ii) for ii in range(7)]
    #     + list(mod_obj.nodes_east[0:7])[::-1]
    # )
    # mod_obj.nodes_north = new_north
    # mod_obj.grid_north -= mod_obj.grid_north.mean()

    # mod_obj.nodes_east = new_east
    # mod_obj.grid_east -= mod_obj.grid_east.mean()

    # mod_obj.grid_center = np.array(
    #     [mod_obj.grid_north.min(), mod_obj.grid_east.min(), 0]
    # )

    # mod_obj.res_model = np.ones(
    #     (mod_obj.nodes_north.size, mod_obj.nodes_east.size, mod_obj.nodes_z.size)
    # )

    if not topography:
        mod_obj.plot_mesh()

    # build 1D model
    if sm_1d is not None:
        for d1, d2, v in sm_1d:
            z_where = np.where((mod_obj.grid_z < d2) & (mod_obj.grid_z >= d1))
            mod_obj.res_model[:, :, z_where] = v

    mod_obj.write_model_file(
        save_path=save_path, model_fn_basename=r"{0}_modem_sm_02.rho".format(fn_stem)
    )


# =============================================================================
#  Center stations
# =============================================================================
if center_stations:
    data_obj.center_stations(mod_obj.model_fn)
    data_obj.write_data_file(
        fn_basename="um_modem_data_z03_c.dat",
        compute_error=False,
        fill=False,
        elevation=True,
    )
### =============================================================================
### Add topography
### =============================================================================
if topography:
    mod_obj.data_obj = data_obj
    mod_obj.add_topography_to_model2(
        topo_fn, airlayer_type="log_down", shift_north=-10300
    )
    mod_obj.res_model[:, -1, :] = mod_obj.res_model[:, -2, :]
    mod_obj.write_model_file(
        model_fn_basename=r"{0}_modem_sm02_topo.rho".format(fn_stem)
    )
    mod_obj.plot_topography()
    mod_obj.plot_mesh(fig_num=2)
    mod_obj.print_mesh_params()

    model_fn = mod_obj.model_fn
    mod_obj = modem.Model()
    mod_obj.read_model_file(model_fn)
    # change data file to have relative topography
    data_obj.center_stations(mod_obj.model_fn)
    sx, sy = data_obj.project_stations_on_topography(mod_obj)

# ==============================================================================
# make the covariance file
# ==============================================================================
if write_cov:
    cov = modem.Covariance()
    cov.smoothing_east = 0.5
    cov.smoothing_north = 0.5
    cov.smoothing_z = 0.5
    cov.smoothing_num = 1

    cov.write_covariance_file(
        os.path.join(save_path, "covariance.cov"), model_fn=mod_obj.model_fn
    )

# # ==============================================================================
# # Write a config file to remember what the parameters are
# # ==============================================================================
# if write_cfg:
#     cfg_obj = modem.ModEM_Config()
#     cfg_obj.add_dict(obj=data_obj)
#     cfg_obj.add_dict(obj=mod_obj)
#     cfg_obj.add_dict(obj=cov)
#     cfg_obj.write_config_file(save_dir=save_path, config_fn_basename="inv_03.cfg")
