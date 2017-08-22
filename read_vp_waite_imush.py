# -*- coding: utf-8 -*-
"""
Created on Mon May 08 13:43:50 2017

@author: jpeacock
"""

import os
import numpy as np
import evtk.hl as a2vtk
from mtpy.utils import array2raster as a2r

vp_fn = r"c:\Users\jpeacock\Documents\iMush\avg16PARA_97x97x35.dat"
sv_path = r"c:\Users\jpeacock\Documents\iMush\waite_2009_depth_slices_vp"

if not os.path.exists(sv_path):
    os.mkdir(sv_path)

vp_dat = np.loadtxt(vp_fn, skiprows=20)

east = np.array(list(sorted(set(vp_dat[:, 0]))))
north = np.array(list(sorted(set(vp_dat[:, 1]))))
depth = np.array(list(sorted(set(vp_dat[:, 4]))))

lat = np.array(list(sorted(set(vp_dat[:, 3]))))
lon = np.array(list(sorted(set(vp_dat[:, 2]))))

vp_shape = (north.size, east.size, depth.size)

vp_arr = np.zeros(vp_shape, dtype=[('vp', np.float),
                                   ('per_vp', np.float),
                                   ('dvp', np.float)])

for line in vp_dat:
    
    ii = np.where(north == line[1])[0][0]
    jj = np.where(east == line[0])[0][0]
    kk = np.where(depth == line[4])[0][0]
    
    vp_arr['vp'][ii, jj, kk] = line[5]
    vp_arr['per_vp'][ii, jj, kk] = line[6]
    vp_arr['dvp'][ii, jj, kk] = line[7]


ll_corner = (lon.min(), lat.min())

for ii, dd in enumerate(depth):
    if ii%2 == 1:
        continue
    a2r.array2raster(os.path.join(sv_path, 
                                  'waite_vp_{0:0.0f}km_wgs84.tif'.format(dd-depth.min())),
                     ll_corner, 
                     500.,
                     500,
                     vp_arr['vp'][:, :, ii])


#vtk_east = np.append(east, east[-1]*1)
#vtk_north = np.append(north, north[-1]*1)
#vtk_depth = np.append(depth, depth[-1]*1)
##vtk_east = east
##vtk_north = north
##vtk_depth = depth
#
#vtk_vp = vp_arr['vp'].T
#vtk_per_vp = vp_arr['per_vp'].T
#vtk_dvp = vp_arr['dvp'].T
#
#a2vtk.gridToVTK(r"c:\Users\jpeacock\Documents\iMush\waite_vp",
#                vtk_north, vtk_east, vtk_depth, 
#                cellData={'vp':vtk_vp,
#                          'vp_per':vtk_per_vp,
#                          'd_vp':vtk_dvp})