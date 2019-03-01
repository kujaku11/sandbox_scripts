# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 13:20:03 2017

read in a winglink out model file, probably better ways to do it, but
this works for now.

@author: jpeacock
"""
# =============================================================================
#  Imports
# =============================================================================
import numpy as np
from mtpy.modeling import modem
#from evtk.hl import gridToVTK

# =============================================================================
# Parameters
# =============================================================================
#fn = r"c:\Users\jpeacock\Documents\Geothermal\Fallon\04_MS_130728_3dmod_it100.out"
fn = r"c:\Users\jpeacock\Downloads\04_MS_130728_3dmod_it100.out"

# =============================================================================
# Read .out file
# =============================================================================
with open(fn, 'r') as fid:
    n_line = fid.readline().strip().split()[0:3]
    nx, ny, nz = [int(nn) for nn in n_line]
    
    dim = np.zeros(nx+ny+nz)
    
    res = np.zeros((nx, ny, nz))
    
    #### get the dimensions of the arrays
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
    
    ### read in x, y, z, res values
    line_len = 10
    index_00 = 0
    index_01 = 1
    count = 0
    z_index = 0
    y_index = 0
    ### the test is for the nearly last lines that has Winglink that ends
    ### the model block
    while n_line[0].lower() != 'winglink':
        n_line = fid.readline().strip().split()
        m = len(n_line)
        if m == 1:
            try:
                z_index = int(n_line[0])-1
            except ValueError:
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
    ### read the last bit which is location information
    loc_lines = fid.readlines()
    location = loc_lines[0].strip().split()[0]
    north, east = [float(value)*1000. for value in loc_lines[2].strip().split()[0:2]]
    rotation = float(loc_lines[3].strip().split()[0])
    max_elev = float(loc_lines[4].strip().split()[0])*1000
        
# =============================================================================
# convert to modem
# =============================================================================
model_obj = modem.Model()
model_obj.nodes_north = x
model_obj.nodes_east = y
model_obj.nodes_z = z

model_obj.res_model = res
model_obj.grid_center = (model_obj.nodes_north.sum()/2., 
                         model_obj.nodes_east.sum()/2.,
                         -1*max_elev)

# if you want to write the modem file uncomment the line putting your directory
# model_obj.write_model_file(save_path=r"save_dir", model_fn_basename='filename')

###        
# now make a vtk grid file
#x_grid = np.array([-x.sum()/2+x[0:ii].sum()for ii in range(x.size)] +[x.sum()/2])
#y_grid = np.array([-y.sum()/2+y[0:ii].sum()for ii in range(y.size)] + [y.sum()/2])
#z_grid = np.array([z[0:ii].sum() for ii in range(z.size)]+[z.sum()]) - max_elev

#gridToVTK(r"c:\Users\jpeacock\Documents\Geothermal\Fallon\wl_04_model",
#          x_grid/1000., 
#          y_grid/1000.,
#          z_grid/1000.,
#          cellData={'resistivity':res})
          