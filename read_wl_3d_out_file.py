# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 13:20:03 2017

read in a winglink out model file, probably better ways to do it, but
this works for now.

x --> varies fastest

@author: jpeacock
"""
 
import numpy as np
from evtk.hl import gridToVTK

fn = r"c:\Users\jpeacock\Documents\Geothermal\Fallon\04_MS_130728_3dmod_it100.out"

with open(fn, 'r') as fid:
    n_line = fid.readline().strip().split()[0:3]
    nx, ny, nz = [int(nn) for nn in n_line]
    
    dim = np.zeros(nx+ny+nz)
    
    res = np.zeros((nx, ny, nz))
    
    count = 0
    index_00 = 0
    index_01 = 1
    m = 2
    while m > 1:
        n_line = fid.readline().strip().split()
        m = len(n_line)
        if count == 0:
            index_01 = m
        dim[index_00:index_01] = np.array([float(nn) for nn in n_line])
        count += 1
        index_00 += m
        index_01 += m
        
    x = dim[0:nx]
    y = dim[nx:nx+ny]
    z = dim[nx+ny:]
    
    line_len = 10
    index_00 = 0
    index_01 = 1
    count = 0
    z_index = 0
    y_index = 0
    while n_line[0].lower() != 'winglink':
        n_line = fid.readline().strip().split()
        m = len(n_line)
        if m == 1:
            try:
                z_index = int(n_line[0])-1
            except ValueError:
                print n_line[0].lower()
                break
            index_00 = 0
            index_01 = 1
            count = 0
            y_index = 0
            continue
        if count == 0:
            index_01 = m
        res[index_00:index_01, y_index, z_index] = np.array([float(nn) for nn in n_line])
        count += 1
        index_00 += m
        index_01 += m
        
        if count*line_len == nx:
            y_index += 1
            index_00 = 0
            index_01 = 1
            count = 0
            
# now make a vtk grid file
x_grid = np.array([-x.sum()/2+x[0:ii].sum()for ii in range(x.size)]+[x.sum()/2])
y_grid = np.array([-y.sum()/2+y[0:ii].sum()for ii in range(y.size)]+[y.sum()/2])
z_grid = np.array([z[0:ii].sum() for ii in range(z.size)]+[z.sum()])

gridToVTK(r"c:\Users\jpeacock\Documents\Geothermal\Fallon\wl_04_model",
          x_grid/1000., 
          y_grid/1000.,
          z_grid/1000.,
          cellData={'resistivity':res})
          
#write a csv file
csv_x = np.array([x[0:ii+1].sum() for ii in range(x.size)])-x[0]
csv_y = np.array([y[0:ii+1].sum() for ii in range(y.size)])-y[0]
csv_z = np.array([z[0:ii+1].sum() for ii in range(z.size)])-z[0]-1225.0
line_list = ['# (0, 0, 0) is the lower left hand corner of the grid at sea level',
             '# northing(m),easting(m),depth(m),resistivity(Ohm-m)']
for z_index, zz in enumerate(csv_z):
    for y_index, yy in enumerate(csv_y):
        for x_index, xx in enumerate(csv_x):
            rr = res[x_index, y_index, z_index]
            line = '{0:.1f},{1:.1f},{2:.1f},{3:.3e}'.format(xx, yy, zz, rr)
            line_list.append(line)
            
with open(r"c:\Users\jpeacock\Documents\Geothermal\Fallon\fallon_mt_3d_model_04.csv", 'w') as fid:
    fid.write('\n'.join(line_list))