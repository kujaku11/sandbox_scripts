# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:52:49 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================

from mtpy.modeling.modem import Model
from mtpy.utils.gis_tools import project_point

# =============================================================================

m = Model()
m.read_model_file(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\modem_inv\inv03\gz_err03_cov02_NLCG_057.rho"
)

casp_epsg = 26742
center = {"lon": -122.828190, "lat": 38.831979, "elev": 1094}
casp_center = project_point(center["lon"], center["lat"], 4326, casp_epsg)
m_to_ft = 3.2808399

# clip model
clip = 8

m.grid_east = m.grid_east[clip:-clip] * m_to_ft
m.grid_north = m.grid_north[clip:-clip] * m_to_ft
m.grid_z = m.grid_z[:-5] * m_to_ft
m.res_model = m.res_model[clip:-clip, clip:-clip, :-5]

m.write_out_file(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\modem_inv\inv03\gz_mt_2017_casp_nad27_zone2_ft.out",
    casp_center[0] * 1000,
    casp_center[1] * 1000,
    center["elev"] * m_to_ft * 1000,
)
