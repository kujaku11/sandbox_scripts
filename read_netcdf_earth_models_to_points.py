# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 15:43:48 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""

import pandas as pd
import numpy as np
import geopandas as gpd
import xarray as xr

# import fiona
from shapely.geometry import Point
from pyevtk.hl import pointsToVTK
from mtpy.utils import gis_tools

# =============================================================================
#
# =============================================================================
fn = r"c:\Users\jpeacock\OneDrive - DOI\earth_models\Moho_Temperature.nc"

nc_obj = xr.open_dataset(fn)

lon, lat = np.meshgrid(nc_obj.longitude, nc_obj.latitude)

x = lon.ravel()
y = lat.ravel()
z = nc_obj.depth.values.ravel()
