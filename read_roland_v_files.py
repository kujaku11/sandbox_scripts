# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 14:36:27 2018

@author: jpeacock
"""

import os
import numpy as np
from pyevtk.hl import gridToVTK
import mtpy.utils.gis_tools as gis_tools
import mtpy.utils.array2raster as a2r

# =============================================================================
# Parameters
# =============================================================================
v_dir = r"c:\Users\jpeacock\Documents\ClearLake\Roland_tomography"
mt_center = (38.83198, -122.8282)

# =============================================================================
# Get files
# =============================================================================
v_fn_list = [os.path.join(v_dir, fn) for fn in os.listdir(v_dir)
             if fn.endswith('.depth')]

z = np.zeros(len(v_fn_list))

for ii, v_fn in enumerate(v_fn_list):
    v = np.loadtxt(v_fn, dtype={'names':('x', 'y', 'lat', 'lon', 'vp', 'vs', 'vpvs'),
                            'formats':(np.float, np.float, np.float, np.float, 
                                       np.float, np.float, np.float)})
    bn = os.path.basename(v_fn)[12:].replace('m', '-')
    z[ii] = float(bn[0:bn.find('k')])
    if ii == 0:
        x = np.array(sorted(list(set(v['x']))))
        y = np.array(sorted(list(set(v['y']))))
        
        # get the cell widths
        dx = x[1]-x[0]
        dy = y[1]-y[0]
        
        center_point = (v['lat'].mean(), v['lon'].mean())
        
        grid_x, grid_y = np.meshgrid(x, y)
        
        vp_arr = np.zeros((x.size, y.size, len(v_fn)))
        vs_arr = np.zeros((x.size, y.size, len(v_fn)))
        vpvs_arr = np.zeros((x.size, y.size, len(v_fn)))

    # fill arrays
    vp_arr[:, :, ii] = v['vp'].reshape(grid_x.shape)
    vs_arr[:, :, ii] = v['vs'].reshape(grid_x.shape)
    vpvs_arr[:, :, ii] = v['vpvs'].reshape(grid_x.shape)
    
    ###--> make shape files
#    a2r.array2raster(os.path.join(v_dir, 
#                                  'vp_depth_slices',
#                                  '{0:02}_vp.tif'.format(ii, z[ii])),
#                    (v['lon'].min(), v['lat'].min()),
#                    dx*1000,
#                    dy*1000,
#                    vp_arr[:, :, ii])
#
#    a2r.array2raster(os.path.join(v_dir, 
#                                  'vs_depth_slices',
#                                  '{0:02}_vs.tif'.format(ii, z[ii])),
#                    (v['lon'].min(), v['lat'].min()),
#                    dx*1000,
#                    dy*1000,
#                    vs_arr[:, :, ii])
#    a2r.array2raster(os.path.join(v_dir, 
#                                  'vpvs_depth_slices',
#                                  '{0:02}_vpvs.tif'.format(ii, z[ii])),
#                    (v['lon'].min(), v['lat'].min()),
#                    dx*1000,
#                    dy*1000,
#                    vpvs_arr[:, :, ii])

# get shifts
mt_east, mt_north, mt_zone = gis_tools.project_point_ll2utm(mt_center[0],
                                                            mt_center[1])
v_east, v_north, v_zone = gis_tools.project_point_ll2utm(center_point[0],
                                                         center_point[1])

shift_east = (mt_east-v_east)/1000.
shift_north = (mt_north-v_north)/1000.

# =============================================================================
# # make vtk arrays
# =============================================================================
vtk_x = np.linspace(x.min()-dx, x.max()+dx, len(x)+1)-shift_east    
vtk_y = np.linspace(y.min()-dy, y.max()+dy, len(y)+1)-shift_north
vtk_z = np.append(z, z[-1])-z[0]    

#gridToVTK(os.path.join(v_dir, 'roland_vp'), 
#          vtk_y, vtk_x, vtk_z,
#          cellData={'Vp':vp_arr})
#
#gridToVTK(os.path.join(v_dir, 'roland_vs'), 
#          vtk_y, vtk_x, vtk_z,
#          cellData={'Vs':vs_arr})
#
#gridToVTK(os.path.join(v_dir, 'roland_vpvs'), 
#          vtk_y, vtk_x, vtk_z,
#          cellData={'VpVs':vpvs_arr})
