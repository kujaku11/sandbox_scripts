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
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\ingenious\modem_inv\inv_01\bm_bv_dv_modem_data_z03_t02.dat"
)

topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\ingenious\northern_ingenious_dem.tiff"

# =============================================================================
# Make data file
# =============================================================================
md = MTData()
md.from_modem(dfn)


# =============================================================================
# build model
# =============================================================================
mod_obj = StructuredGrid3D(
    station_locations=md.station_locations, center_point=md.center_point
)

mod_obj.cell_size_east = 1500
mod_obj.cell_size_north = 1500
mod_obj.pad_east = 7
mod_obj.pad_north = 7
mod_obj.pad_num = 4
mod_obj.ew_ext = 200000
mod_obj.ns_ext = 200000
mod_obj.z_mesh_method = "default"
mod_obj.z_bottom = 200000
mod_obj.z_target_depth = 70000
mod_obj.pad_z = 5
mod_obj.n_air_layers = 45
mod_obj.n_layers = 100
mod_obj.z1_layer = 30
mod_obj.pad_stretch_v = 1.85
mod_obj.z_layer_rounding = 1
mod_obj.res_initial_value = 50

mod_obj.make_mesh()
mod_obj.add_topography_to_model(
    topography_file=topo_fn, max_elev=2600, airlayer_type="constant"
)

md.center_stations(mod_obj)
md.project_stations_on_topography(mod_obj)
md.to_modem(dfn.parent.joinpath(f"{dfn.stem}_topo.dat"))
mod_obj.station_locations = md.station_locations

mod_obj.plot_mesh()

mod_obj.to_modem(
    save_path=dfn.parent,
    model_fn_basename=f"bvmbdv_sm{mod_obj.res_initial_value}_topo.rho",
)


cov = Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.5
cov.smoothing_north = 0.5
cov.smoothing_z = 0.5
cov.smoothing_num = 1

cov.write_covariance_file(
    dfn.parent.joinpath("covariance.cov"), res_model=mod_obj.res_model
)
