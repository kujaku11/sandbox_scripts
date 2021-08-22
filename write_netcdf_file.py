# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 15:05:19 2017

@author: jrpeacock
"""

import netCDF4
import mtpy.modeling.modem as modem
import mtpy.utils.gis_tools as gis_tools
import numpy as np

mfn = r"c:\Users\jrpeacock\Google Drive\LV_Geothermal\SI_Peacock_etal2016_D2.rho"

model_center = (38.0, -115.0)
model_center_ne = gis_tools.project_point_ll2utm(model_center[0], model_center[1])

m_obj = modem.Model()
m_obj.read_model_file(mfn)

# need to make a lat and lon list
lat = np.zeros(m_obj.nodes_north.size)
lon = np.zeros(m_obj.nodes_east.size)

for ii, north in enumerate(model_center_ne[0] - m_obj.grid_north[:-1]):
    lat_00, lon_00 = gis_tools.project_point_utm2ll(
        north, model_center_ne[1], model_center_ne[2]
    )
    lat[ii] = lat_00

for ii, east in enumerate(model_center_ne[1] - m_obj.grid_east[:-1]):
    lat_00, lon_00 = gis_tools.project_point_utm2ll(
        model_center_ne[0], east, model_center_ne[2]
    )
    lon[ii] = lon_00

# nc_obj = netCDF4.Dataset(m_obj.model_fn[:-4]+'.nc', 'w', format='NETCDF4')
nc_obj = netCDF4.Dataset(r"c:\Users\jrpeacock\test_01.nc", "w", format="NETCDF4")
nc_obj.setncattr("description", "Resistivity Model from ModEM")

# dimensions
nc_lat = nc_obj.createDimension("latitude", lat.size)
nc_lon = nc_obj.createDimension("longitude", lon.size)
nc_depth = nc_obj.createDimension("depth", m_obj.grid_z.size - 1)

# variables
nc_lats = nc_obj.createVariable("latitude", "f8", ("latitude",))
nc_lons = nc_obj.createVariable("longitude", "f8", ("longitude",))
nc_depths = nc_obj.createVariable("depth", "f8", ("depth",))
nc_res = nc_obj.createVariable("resistivity", "f8", ("latitude", "longitude", "depth"))
nc_lats[:] = lat
nc_lons[:] = lon
nc_depths[:] = m_obj.grid_z[:-1]
nc_res[:] = m_obj.res_model

nc_lats.units = "degrees"
nc_lons.units = "degrees"
nc_depths.units = "kilometers"

nc_obj.close()
