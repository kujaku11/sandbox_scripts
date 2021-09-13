# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 15:05:19 2017

@author: jrpeacock
"""

from pathlib import Path
import mtpy.modeling.modem as modem
import mtpy.utils.gis_tools as gis_tools
import numpy as np
import xarray as xr

mfn = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_09\um_z05_c025_086.rho")

model_center = (45.654713,  -118.547148)
model_center_ne = gis_tools.project_point_ll2utm(
    model_center[0], model_center[1], epsg=26911)

m_obj = modem.Model()
m_obj.read_model_file(mfn)

x = xr.DataArray(m_obj.res_model, 
                 dims=("northing", "easting", "depth"),
                 coords={
                     "northing": m_obj.grid_north[:-1] + model_center_ne[0],
                     "easting": m_obj.grid_east[:-1] + model_center_ne[1],
                     "depth": m_obj.grid_z[:-1]},
                 attrs={"distance_units": "meters",
                        "resistivity_units": "ohm-meters",
                        "model_center_ll": model_center,
                        "model_center_utm": model_center_ne,
                        "datum": "NAD83",
                        "description": "electrical resistivity"})
x.name = "resistivity"
x.to_netcdf(mfn.parent.joinpath("ctuir_phase2_resistivity_model.nc"))


# # nc_obj = netCDF4.Dataset(m_obj.model_fn[:-4]+'.nc', 'w', format='NETCDF4')
# nc_obj = netCDF4.Dataset(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_09\um_z05_c025_086.nc", "w", format="NETCDF4")
# nc_obj.setncattr("description", "Resistivity Model from ModEM")

# # dimensions
# nc_lat = nc_obj.createDimension("latitude", lat.size)
# nc_lon = nc_obj.createDimension("longitude", lon.size)
# nc_depth = nc_obj.createDimension("depth", m_obj.grid_z.size - 1)

# # variables
# nc_lats = nc_obj.createVariable("latitude", "f8", ("latitude",))
# nc_lons = nc_obj.createVariable("longitude", "f8", ("longitude",))
# nc_depths = nc_obj.createVariable("depth", "f8", ("depth",))
# nc_res = nc_obj.createVariable("resistivity", "f8", ("latitude", "longitude", "depth"))
# nc_lats[:] = lat
# nc_lons[:] = lon
# nc_depths[:] = m_obj.grid_z[:-1]
# nc_res[:] = m_obj.res_model

# nc_lats.units = "degrees"
# nc_lons.units = "degrees"
# nc_depths.units = "kilometers"

# nc_obj.close()
