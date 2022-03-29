# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 16:29:24 2022

@author: jpeacock
"""

from pathlib import Path
import xarray as xr
import numpy as np
import pyproj
from mtpy.modeling.modem import Model, Data


inv_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\EasternMojave\modem_inv\inv_01"
)

m = Model()
m.read_model_file(inv_path.joinpath("mj_z05_t02_c03_126.rho"))

d = Data()
d.read_data_file(inv_path.joinpath(r"mj_z05_t02_c03_126.dat"))
center = d.center_point

pad = 12
model_epsg = 32611


class CenterPoint:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# great basin center
# center = CenterPoint(**{"latitude": 38.615252,
#                 "longitude": -119.015192,
#                 "easting": 324551.82381348,
#                 "northing": 4276008.10412004,
#                 "elevation": 0.,
#                 "utm_zone":"10S",
#                 "model_epsg": "32611"})

# need to project points onto a lat/lon grid
model_crs = pyproj.CRS(f"epsg:{model_epsg}")
x_crs = pyproj.CRS("epsg:4326")

translator = pyproj.Transformer.from_crs(model_crs, x_crs)

east, north = np.broadcast_arrays(
    m.grid_north[pad : -(pad + 1), None] + center.north,
    m.grid_east[None, pad : -(pad + 1)] + center.east,
)


lat, lon = translator.transform(north.ravel(), east.ravel())

latitude = np.linspace(lat.min(), lat.max(), east.shape[0])
longitude = np.linspace(lon.min(), lon.max(), east.shape[1])
depth = (m.grid_z[:-1] + center.elev) / 1000

# need to have longitude first
x_res = np.swapaxes(np.log10(m.res_model[pad:-pad, pad:-pad, :]), 0, 1).T
x = xr.DataArray(
    x_res,
    coords=[("depth", depth), ("latitude", latitude), ("longitude", longitude),],
    dims=["depth", "latitude", "longitude"],
)

x.name = "electrical_resistivity"
x.attrs["long_name"] = "electrical resistivity"
x.attrs["units"] = "Ohm-m"
x.attrs["standard_name"] = "resistivity"
x.attrs["display_name"] = "log10(resistivity)"


# metadata for coordinates
x.coords["latitude"].attrs["long_name"] = "Latitude; positive_north"
x.coords["latitude"].attrs["units"] = "degrees_north"
x.coords["latitude"].attrs["standard_name"] = "Latitude"

x.coords["longitude"].attrs["long_name"] = "longitude; positive_east"
x.coords["longitude"].attrs["units"] = "degrees_east"
x.coords["longitude"].attrs["standard_name"] = "longitude"

x.coords["depth"].attrs["long_name"] = "depth; positive_down"
x.coords["depth"].attrs["display_name"] = "depth"
x.coords["depth"].attrs["units"] = "km"
x.coords["depth"].attrs["standard_name"] = "depth"

ds = xr.Dataset(*[{"resistivity": x}])


# fill in some metadata

ds.attrs["Conventions"] = "CF-1.0"
ds.attrs["Metadata_Conventions"] = "Unidata Dataset Discovery v1.0"
ds.attrs[
    "title"
] = "Electrical resistivity of the Great Basin from magnetotelluric data"
ds.attrs["id"] = "GB_MT_2022"
ds.attrs[
    "summary"
] = "A 3D electrical resistivity model of the Great Basin in the western US derived from magnetotelluric data using the inversion software ModEM."
ds.attrs["keywords"] = "electrical resistivity, Great Basin"
ds.attrs["Conventions"] = "CF-1.0"
ds.attrs["Metadata_Conventions"] = "Unidata Dataset Discovery v1.0"
ds.attrs["author_name"] = "Jared Peacock"
ds.attrs["author_url"] = ""
ds.attrs["author_email"] = "jpeacock@usgs.gov"
ds.attrs["institution"] = "US Geological Survey"
ds.attrs["repository_name"] = ("",)
ds.attrs["repository_institution"] = ("",)
ds.attrs["repository_pid"] = ("",)
ds.attrs[
    "acknowledgment"
] = "Data were collected by various researchers over the last 30 years."
ds.attrs["references"] = "Peacock et al."
ds.attrs["history"] = "First version 2022-03-04"
ds.attrs["comment"] = "Model has not been tested for sensitivity, use with caution"
ds.attrs[
    "NCO"
] = "netCDF Operators version 4.7.5 (Homepage = http://nco.sf.net, Code=http://github/nco/nco"

# geospatial metadata
ds.attrs["geospatial_lat_min"] = latitude.min()
ds.attrs["geospatial_lat_max"] = latitude.max()
ds.attrs["geospatial_lat_units"] = "degrees_north"
ds.attrs["geospatial_lat_resolution"] = np.diff(latitude).mean()

ds.attrs["geospatial_lon_min"] = longitude.min()
ds.attrs["geospatial_lon_max"] = longitude.max()
ds.attrs["geospatial_lon_units"] = "degrees_east"
ds.attrs["geospatial_lon_resolution"] = np.diff(longitude).mean()

ds.attrs["geospatial_vertical_min"] = depth.min()
ds.attrs["geospatial_vertical_max"] = depth.max()
ds.attrs["geospatial_vertical_units"] = "km"
ds.attrs["geospatial_vertical_positive"] = "down"


ds.to_netcdf(path=inv_path.joinpath("mj_z05_t02_c03_126.nc"))
