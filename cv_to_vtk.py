# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 15:06:47 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from mtpy.modeling import StructuredGrid3D

# =============================================================================

s = StructuredGrid3D()
s.from_modem(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\cv_inv_01\cv_z03_t02_c025_086.rho"
)
s.center_point.latitude = 37.823699
s.center_point.longitude = -117.666829
s.center_point.utm_epsg = 32611

s.to_vtk(
    geographic_coordinates=True,
    units="m",
    coordinate_system="enz-",
    vtk_fn_basename="cv_enzm",
)
