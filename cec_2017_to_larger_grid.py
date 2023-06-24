# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 10:00:06 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from mtpy import MTData
from mtpy.modeling import StructuredGrid3D

# =============================================================================
model_center = {
    "latitude": 38.812566,
    "longitude": -122.796391,
    "elevation": -1150.00,
}

model_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2021\gz_sm02_topo.rho"
data_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\modem_inv\inv03\gz_data_err03_tec_edit_topo.dat"

model_obj = StructuredGrid3D()
model_obj.read_modem_file(model_fn)


md = MTData()
md.from_modem_data(data_fn)
md._center_lat = model_center["latitude"]
md._center_lon = model_center["longitude"]
md._center_elev = model_center["elevation"]
md.utm_epsg = 32610

md.compute_relative_locations()
md.center_stations(model_obj)
md.project_stations_on_topography(model_obj)

model_obj.station_locations = md.station_locations
model_obj.plot_mesh()
