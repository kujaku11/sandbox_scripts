# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 16:05:35 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import numpy as np
from mtpy import MTCollection, MTData
from mtpy.modeling import StructuredGrid3D
from mtpy.modeling.modem import Covariance

# =============================================================================

dfn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\SAGE\modem_inv\vc02_topo\VC_2024_ZT_data_edit.dat"
)
# topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\westcoast_etopo.asc"
topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\SAGE\valles_topo.tiff"

# =============================================================================
# Make data file
# =============================================================================
if not dfn.exists():
    raise FileNotFoundError(f"Could not find {dfn}.")
else:
    md = MTData()
    md.from_modem(dfn)
    md._center_lat = None
    md._center_lon = None
    md.utm_crs = 32613
    md.compute_relative_locations()


# =============================================================================
# build model
# =============================================================================
mod_obj = StructuredGrid3D(
    station_locations=md.station_locations, center_point=md.center_point
)

mod_obj.cell_size_east = 500
mod_obj.cell_size_north = 500
mod_obj.pad_east = 13
mod_obj.pad_north = 13
mod_obj.pad_num = 4
mod_obj.ew_ext = 200000
mod_obj.ns_ext = 200000
mod_obj.z_mesh_method = "default"
mod_obj.z_bottom = 200000
mod_obj.z_target_depth = 60000
mod_obj.pad_z = 5
mod_obj.n_air_layers = 60
mod_obj.n_layers = 110
mod_obj.z1_layer = 25
mod_obj.pad_stretch_v = 1.85
mod_obj.z_layer_rounding = 1
mod_obj.res_initial_value = 70

mod_obj.make_mesh()
mod_obj.add_topography_to_model(
    topography_file=topo_fn,
    max_elev=3375,
    airlayer_type="constant",
    shift_east=0,  # -1200,
)

md.center_stations(mod_obj)
md.project_stations_on_topography(mod_obj)
md.to_modem(dfn.parent.joinpath(f"{dfn.stem}_topo.dat"))
mod_obj.station_locations = md.station_locations

mod_obj.plot_mesh()

mod_obj.to_modem(
    save_path=dfn.parent,
    model_fn_basename="vc_sm70_topo.rho",
)


cov = Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.5
cov.smoothing_north = 0.5
cov.smoothing_z = 0.5
cov.smoothing_num = 1

cov.write_covariance_file(
    dfn.parent.joinpath("covariance.cov"), res_model=mod_obj.res_model
)
