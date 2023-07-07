# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 10:00:06 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import numpy as np

from mtpy import MTData
from mtpy.modeling import StructuredGrid3D

# =============================================================================
model_center = {
    "latitude": 38.812566,
    "longitude": -122.796391,
    "elevation": -1150.00,
}

model_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2021\gz_sm02_topo.rho"

edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2023_EDI_files_birrp_processed\GeographicNorth_rr_frn\updated"
)


model_obj = StructuredGrid3D()
model_obj.read_modem_file(model_fn)


md = MTData()
md.add_station(list(edi_path.glob("*.edi")))
md.interpolate(
    np.logspace(-np.log10(500), np.log10(1023), num=23), inplace=True
)

md.z_model_error.error_value = 0.03
md.z_model_error.error_type = "eigen"

md.compute_model_errors()

md._center_lat = model_center["latitude"]
md._center_lon = model_center["longitude"]
md._center_elev = model_center["elevation"]
md.utm_epsg = 32610

md.compute_relative_locations()
md.center_stations(model_obj)
md.project_stations_on_topography(model_obj)

md.to_modem_data(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2023\gz_2022_modem_data_z03_tec.dat"
)

model_obj.station_locations = md.station_locations
model_obj.plot_mesh()
