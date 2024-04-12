# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 17:20:17 2016

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import os
from pathlib import Path
import numpy as np
import pandas as pd

from mtpy.core import MTLocation
from mtpy.modeling import StructuredGrid3D
from mtpy.modeling.modem import Covariance

# =============================================================================
# Parameters
# =============================================================================
data_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_03\gb_modem_data_z05_t02.dat"
)
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_03"
)
topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\westcoast_etopo.asc"

fn_stem = "gb"

model_epsg = 32611

center_point = MTLocation(
    latitude=37.855540, longitude=-116.897222, utm_epsg=model_epsg
)
station_locations = pd.read_csv(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_03\gb_station_locations.csv"
)

# directives on what to do
write_data = False
write_model = True
write_cov = True
topography = True
center_stations = False

if not save_path.exists():
    save_path.mkdir()

# ==============================================================================
# Make the data file
# ==============================================================================

# data_obj = MTData()
# data_obj.from_modem(data_fn)
# data_obj.utm_crs = 32611
# ==============================================================================
# First make the mesh
# ==============================================================================
if write_model:
    mod_obj = StructuredGrid3D(
        station_locations=station_locations,
        center_point=center_point,
    )
    mod_obj.cell_size_east = 7000
    mod_obj.cell_size_north = 7000
    mod_obj.pad_num = 3
    mod_obj.pad_east = 10
    mod_obj.pad_north = 10
    mod_obj.pad_method = "extent1"
    mod_obj.z_mesh_method = "default"
    mod_obj.pad_stretch_h = 1.2
    mod_obj.pad_stretch_v = 1.25
    mod_obj.ew_ext = 2.6e6
    mod_obj.ns_ext = 2.6e6
    mod_obj.pad_z = 8
    mod_obj.n_layers = 70
    # setting this to none will force to only add bathymetry
    mod_obj.n_air_layers = None
    mod_obj.z1_layer = 30
    mod_obj.z_target_depth = 250000.0
    mod_obj.z_bottom = 800000.0
    mod_obj.res_initial_value = 70.0

    # --> here is where you can rotate the mesh
    mod_obj.mesh_rotation_angle = 0.0

    mod_obj.make_mesh()

    mod_obj.res_model[:] = mod_obj.res_initial_value

    if not topography:
        mod_obj.plot_mesh()
        mod_obj.to_modem(
            model_fn=save_path.joinpath(
                f"{fn_stem}_sm{np.log10(mod_obj.res_initial_value):02.0f}.rho"
            )
        )

# =============================================================================
# Add topography
# =============================================================================
if topography:
    mod_obj.add_topography_to_model(
        topo_fn, airlayer_type="log_down", shift_north=0, shift_east=0
    )
    mod_obj.to_modem(
        model_fn=save_path.joinpath(
            f"{fn_stem}_sm{np.log10(mod_obj.res_initial_value):02.0f}_topo.rho"
        )
    )
    mod_obj.plot_mesh()

    # change data file to have relative topography
    # if center_stations:
    #     data_obj.center_stations(mod_obj)
    # data_obj.project_stations_on_topography(mod_obj)

# ==============================================================================
# make the covariance file
# ==============================================================================
if write_cov:
    cov = Covariance(grid_dimensions=mod_obj.res_model.shape)
    cov.smoothing_east = 0.6
    cov.smoothing_north = 0.6
    cov.smoothing_z = 0.6
    cov.smoothing_num = 1

    if topography:
        cov.write_covariance_file(
            cov_fn=save_path.joinpath("covariance_topo.cov"),
        )
    else:
        cov.write_covariance_file(
            cov_fn=save_path.joinpath("covariance.cov"),
        )

    # mod_obj.write_vtk_file(
    #     vtk_save_path=save_path, vtk_fn_basename="{0}_sm".format(fn_stem)
    # )

    # data_obj.data_array["elev"] = data_obj.data_array["rel_elev"]
    # data_obj.write_vtk_station_file(
    #     vtk_save_path=save_path, vtk_fn_basename="{0}_stations".format(fn_stem)
    # )

    # mod_obj.print_mesh_params()
