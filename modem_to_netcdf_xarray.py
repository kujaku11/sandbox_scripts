# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 16:29:24 2022

@author: jpeacock
"""

from pathlib import Path
import xarray as xr
import numpy as np
import pyproj
from mtpy.modeling.modem import Model


inv_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_01")

m = Model()
m.read_model_file(inv_path.joinpath("gb_z03_t02_c02_046.rho"))

pad = 10


class CenterPoint:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

# great basin center
center = CenterPoint(**{"latitude": 38.615252,
                "longitude": -119.015192,
                "easting": 324551.82381348,
                "northing": 4276008.10412004,
                "elevation": 0.,
                "utm_zone":'11S',
                "model_epsg": "32611"})

# need to project points onto a lat/lon grid
model_crs = pyproj.CRS(f"epsg:{center.model_epsg}")
x_crs = pyproj.CRS("epsg:4326")

translator = pyproj.Transformer.from_crs(model_crs, x_crs)

east, north = np.broadcast_arrays(m.grid_north[pad:-(pad+1), None] + center.northing,
                                  m.grid_east[None, pad:-(pad+1)] + center.easting)


lat, lon = translator.transform(north.ravel(), east.ravel())

latitude = np.linspace(lat.min(), lat.max(), east.shape[0])
longitude = np.linspace(lon.min(), lon.max(), east.shape[1])
depth = (m.grid_z[:-1] + center.elevation) / 1000


x = xr.DataArray(np.log10(m.res_model[pad:-pad, pad:-pad, :]), 
                 coords=[("latitude", latitude), 
                       ("longitude", longitude),
                       ("depth", depth)],
                 dims=["latitude", "longitude", "depth"])

x.name = "electrical_resistivity"
x.attrs["long_name"] = "electrical resistivity"
x.attrs["units"] = "log10(Ohm-m)"
x.attrs["standard_name"] = "resistivity"
x.attrs["display_name"] = "resistivity"
x.attrs["Conventions"] = "CF-1.0"
x.attrs["Metadata_Conventions"] = "Unidata Dataset Discovery v1.0"

# metadata for coordinates
x.coords["latitude"].attrs["long_name"] = "Latitude; positive_north"
x.coords["latitude"].attrs["units"] = "degrees"
x.coords["latitude"].attrs["standard_name"] = "Latitude"

x.coords["longitude"].attrs["long_name"] = "longitude; positive_east"
x.coords["longitude"].attrs["units"] = "degrees"
x.coords["longitude"].attrs["standard_name"] = "longitude"

x.coords["depth"].attrs["long_name"] = "depth; positive_down"
x.coords["depth"].attrs["display_name"] = "depth"
x.coords["depth"].attrs["units"] = "km"
x.coords["depth"].attrs["standard_name"] = "depth"

# ds = xr.Dataset(*[{"resistivity": x}])


# fill in some metadata                 


x.attrs["title"] = "Electrical resistivity of the Great Basin from magnetotelluric data"
x.attrs["id"] = "GB_MT_2022"
x.attrs["summary"] = "A 3D electrical resistivity model of the Great Basin in the western US derived from magnetotelluric data using the inversion software ModEM."
x.attrs["keywords"] = "electrical resistivity, Great Basin"
x.attrs["Conventions"] = "CF-1.0"
x.attrs["Metadata_Conventions"] = "Unidata Dataset Discovery v1.0"
x.attrs["creator_name"] = "Jared Peacock"
x.attrs["creator_url"] = ""
x.attrs["creator_email"] = "jpeacock@usgs.gov"
x.attrs["institution"] = "US Geological Survey"
x.attrs["acknowledgment"] = "Data were collected by various researchers over the last 30 years."
x.attrs["reference"] = "Peacock et al."
x.attrs["history"] = "First version 2022-03-04" 
x.attrs["comment"] = "Model has not been tested for sensitivity, use with caution"
x.attrs["NCO"] = "netCDF Operators version 4.7.5 (Homepage = http://nco.sf.net, Code=http://github/nco/nco"

# geospatial metadata
x.attrs["geospatial_lat_min"] = latitude.min()
x.attrs["geospatial_lat_max"] = latitude.max()
x.attrs["geospatial_lat_units"] = "degrees_north"
x.attrs["geospatial_lat_resolution"] = np.diff(latitude).mean()

x.attrs["geospatial_lon_min"] = longitude.min()
x.attrs["geospatial_lon_max"] = longitude.max()
x.attrs["geospatial_lon_units"] = "degrees_east"
x.attrs["geospatial_lon_resolution"] = np.diff(longitude).mean()

x.attrs["geospatial_vertical_min"] = depth.min()
x.attrs["geospatial_vertical_max"] = depth.max()
x.attrs["geospatial_vertical_units"] = "km"
x.attrs["geospatial_vertical_positive"] = "down"


x.to_netcdf(path=inv_path.joinpath("gb_z03_t02_c02_046_x.nc"))




