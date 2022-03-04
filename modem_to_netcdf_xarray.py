# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 16:29:24 2022

@author: jpeacock
"""

from pathlib import Path
import xarray as xr
import numpy as np
from mtpy.modeling.modem import Model, Data

inv_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_01")

m = Model()
m.read_model_file(inv_path.joinpath("gb_z03_t02_c02_046.rho"))

# great basin center
center_point = (38.615252, -119.015192,  324551.82381348,  4276008.10412004,  0., '11S')

x = xr.DataArray(m.res_model, 
                 coords=[("northing", m.grid_north[:-1] + center_point[3]), 
                       ("easting", m.grid_east[:-1] + center_point[2]),
                       ("depth", m.grid_z[:-1] + center_point[4])],
                 dims=["northing", "easting", "depth"])
                 
x.name = "electrical resistivity"

x.to_netcdf(path=inv_path.joinpath("gb_z03_t02_c02_046.nc"))




