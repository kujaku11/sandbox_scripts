# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 10:38:02 2017

@author: jrpeacock
"""

import netCDF4
import numpy as np
import mtpy.utils.gis_tools as gis_tools
import mtpy.utils.array2raster as a2r
from evtk.hl import gridToVTK
import os

nc_fn = r"c:\Users\jpeacock\Documents\iMush\vp_depth_slices_ulberg\ulbergVPmodel_Run_124.nc"

nc_obj = netCDF4.Dataset(nc_fn, 'r')

depth = nc_obj.variables['depth'][:]
lat = nc_obj.variables['latitude'][:]
lon = nc_obj.variables['longitude'][:]

vp = np.nan_to_num(nc_obj.variables['vp'][:])
dvp = np.nan_to_num(nc_obj.variables['dvp_ulberg'][:])

# the arrays are (depth, lat, lon) --> (z, y, x)
# taking the transpose will give (lon, lat, depth) --> (x, y, z)

lower_left = gis_tools.project_point_ll2utm(lat.min(), lon.min())
upper_right = gis_tools.project_point_ll2utm(lat.max(), lon.max())

d_east = (upper_right[0]-lower_left[0])/lon.size
d_north = (upper_right[1]-lower_left[1])/lat.size

east = np.arange(lower_left[0], upper_right[0]+d_east, d_east)/1000.
north = np.arange(lower_left[1], upper_right[1], d_north)/1000.

#for zz in range(depth.size):
#    raster_fn = os.path.join(r"c:\Users\jpeacock\Documents\iMush\vp_depth_slices_ulberg",
#                             "{0:02}_vp_{1:.0f}_WGS84.tif".format(zz, depth[zz]))
#    raster_fn = raster_fn.replace('-', 'm')
#    a2r.array2raster(raster_fn, 
#                     (float(lon.min()), float(lat.min())), 
#                     1730.0, 
#                     1202.0, 
#                     (vp[zz, :, :]))



vtk_vp = np.zeros((lat.size, lon.size, depth.size))
vtk_dvp = np.zeros((lat.size, lon.size, depth.size))
for z_index in range(depth.size):
    vtk_vp[:, :, z_index] = vp[z_index, ::-1, ::-1]
    vtk_dvp[:, :, z_index] = dvp[z_index, ::-1, ::-1]
    
mt_east, mt_north, mt_zone = gis_tools.project_point_ll2utm(46.44891,
                                                            -122.031869)
msh_east, msh_north, msh_zone = gis_tools.project_point_ll2utm(46.199109,
                                                               -122.188576)

d_east = (mt_east-msh_east)/1000.+7
d_north = (mt_north-msh_north)/1000.+18
depth = np.append(depth, depth[-1]+(depth[-1]-depth[-2]))
gridToVTK(r"c:\Users\jpeacock\Documents\iMush\imush_ulberg_velocity", 
          msh_north/1000.-north-d_north,
          msh_east/1000.-east-d_east,
          depth,
          cellData={'vp':vtk_vp,
                    'd_vp':vtk_dvp})
    
#gridToVTK(r"c:\Users\jpeacock\Documents\iMush\imush_ulberg_velocity", 
#          north-msh_north/1000.+d_north/1000.,
#          east-msh_east/1000.+d_east/1000.,
#          depth,
#          cellData={'vp':vtk_vp,
#                    'd_vp':vtk_dvp})
#
#nc_obj.variables['latitude'][:] = north
#nc_obj.variables['longitude'][:] = east

#w_nc_fid = netCDF4.Dataset('c:\Users\jrpeacock\Google Drive\MSH\ulbergVPmodel_en.nc',
#                           'w', format='NETCDF4')
#
## Using our previous dimension information, we can create the new dimensions
#data = {}
#for dim in nc_obj.dimensions:
#    w_nc_fid.createDimension(dim, nc_obj.variables[dim].size)
#    data[dim] = w_nc_fid.createVariable(dim, nc_obj.variables[dim].dtype,\
#                                        (dim,))
#    # You can do this step yourself but someone else did the work for us.
#    for ncattr in nc_obj.variables[dim].ncattrs():
#        data[dim].setncattr(ncattr, nc_obj.variables[dim].getncattr(ncattr))
#for var in ['vp', 'd_vp']:
#    w_nc_fid.createVariable(var, 'f8', ('depth', 'latitude', 'longitude'))
#    
## Assign the dimension data to the new NetCDF file.
#w_nc_fid.variables['latitude'][:] = north
#w_nc_fid.variables['longitude'][:] = east
#w_nc_fid.variables['vp'][:] = vp
#w_nc_fid.variables['d_vp'][:] = dvp
#
#w_nc_fid.close()  # close the new file


#gridToVTK(vtk_fn, 
#         self.grid_north/1000., 
#         self.grid_east/1000.,
#         self.grid_z/1000.,
#         cellData={'resistivity':self.res_model}) 