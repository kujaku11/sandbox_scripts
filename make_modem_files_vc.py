# -*- coding: utf-8 -*-
"""
Created on Sat Aug  5 12:31:47 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from mtpy import MTData
from mtpy.modeling import StructuredGrid3D
from mtpy.modeling.modem import Covariance

# =============================================================================

topo_fn = r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\westcoast_etopo.asc"

data = MTData()
data.from_modem_data(
    r"c:\Users\jpeacock\OneDrive - DOI\SAGE\modem_inv\vc_01\vc_modem_data_z05_t02.dat"
)

mod_obj = StructuredGrid3D(
    station_locations=data.station_locations, center_point=data.center_point
)

mod_obj.cell_size_east = 500
mod_obj.cell_size_north = 500
mod_obj.pad_east = 7
mod_obj.pad_north = 7
mod_obj.pad_num = 4
mod_obj.ew_ext = 200000
mod_obj.ns_ext = 200000
mod_obj.z_mesh_method = "default"
mod_obj.z_bottom = 200000
mod_obj.z_target_depth = 70000
mod_obj.pad_z = 5
mod_obj.n_air_layers = 15
mod_obj.n_layers = 60
mod_obj.z1_layer = 30
mod_obj.pad_stretch_v = 1.5
mod_obj.z_layer_rounding = 1

# --> here is where you can rotate the mesh
mod_obj.mesh_rotation_angle = 0

mod_obj.make_mesh()
mod_obj.add_topography_to_model(topography_file=topo_fn)

data.project_stations_on_topography(mod_obj)
mod_obj.station_locations = data.station_locations

mod_obj.plot_mesh()

mod_obj.write_modem_file(
    save_path=r"c:\Users\jpeacock\OneDrive - DOI\SAGE\modem_inv\vc_01",
    model_fn_basename="vc_sm02_topo.rho",
)


cov = Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.5
cov.smoothing_north = 0.5
cov.smoothing_z = 0.5
cov.smoothing_num = 1

cov.write_covariance_file(
    r"c:\Users\jpeacock\OneDrive - DOI\SAGE\modem_inv\vc_01\covariance.cov",
    model_fn=mod_obj.model_fn,
)
