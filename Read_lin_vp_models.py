# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 06:56:58 2015

@author: jpeacock
"""

import os
import numpy as np
import evtk.hl as a2vtk
import mtpy.utils.latlongutmconversion as ll2utm

vp_fn = r"c:\Users\jpeacock\Documents\LV\Lin_Vp_model.txt"
#vp_fn = r"c:\Users\jpeacock\Documents\LV\Lin_VpVs_model.txt"
block_len = 6
cell_size = 3.0
#mt_center = (-118.872, 37.688)
#mt_center = (-118., 37.688)
#mt_zone, mt_east, mt_north = ll2utm.LLtoUTM(23, mt_center[1], mt_center[0])
mt_east = 336800
mt_north = 4167525

vfid = file(vp_fn, 'r')
line = vfid.readlines()[0].split()
n_vp = len(line)
vfid.close()

v_array = np.array(line, dtype=np.float)
v_array = v_array.reshape((n_vp/block_len, block_len))

vel_arr = np.zeros(n_vp/block_len, dtype=[('lon', np.float),
                                          ('lat', np.float),
                                          ('depth', np.float),
                                          ('east', np.float),
                                          ('north', np.float),
                                          ('Vp', np.float)])
for ii in range(n_vp/block_len):
    vel_arr[ii] = v_array[ii, :]


#need to make a simple grid in each direction
#VTK needs the grid to n+1 larger than the data 
east = np.arange(vel_arr['east'].min(), vel_arr['east'].max()+2*cell_size,
                 cell_size)
north = np.arange(vel_arr['north'].min(), vel_arr['north'].max()+2*cell_size,
                  cell_size)
                  
# z has un equal spacing so need to extract the values from the data
z = np.append(np.array(sorted(set(vel_arr['depth']))), vel_arr['depth'].max()+4)

#create dictionaries to get the indexes correct for putting it in 
# a right hand coordinate system with Z + down              
east_index_dict = dict([(xkey, xvalue) for xvalue, xkey in enumerate(east)])
north_index_dict = dict([(ykey, yvalue) for yvalue, ykey in enumerate(north)])
z_index_dict = dict([(zkey, zvalue) for zvalue, zkey in enumerate(z)])

n_east = east.shape[0]-1
n_north = north.shape[0]-1
n_z = z.shape[0]-1

model_vel = np.zeros((n_north, n_east, n_z))
model_vel_change = np.zeros((n_north, n_east, n_z))

# lin has west as positive and east as negative 
for v_arr in vel_arr:
    e_index = east_index_dict[v_arr['east']*-1]
    n_index = north_index_dict[v_arr['north']]
    z_index = z_index_dict[v_arr['depth']]
    v_avg = vel_arr[np.where(vel_arr[:]['depth']==v_arr['depth'])]['Vp'].mean() 
    model_vel[n_index, e_index, z_index] = v_arr['Vp']
    model_vel_change[n_index, e_index, z_index] = 100*((v_arr['Vp']-v_avg)/v_avg)

# find the shift between the center of each grid    
v_zone, v_east, v_north = ll2utm.LLtoUTM(23, 
                                         vel_arr['lat'].mean(), 
                                         vel_arr['lon'].mean())
                                         
shift_east = (v_east-mt_east)/1000.
shift_north = (v_north-mt_north)/1000.

#vel.reshape()
a2vtk.gridToVTK(os.path.join(os.path.dirname(vp_fn), 'lv_3d_models', 
                             'lin2015_vp_lvc'), 
                north+shift_north,
                east+shift_east, 
                z+2, 
                cellData={'Vp':model_vel, 
                          'Vp_change':model_vel_change})    
#a2vtk.gridToVTK(os.path.join(os.path.dirname(vp_fn), 'lin2015_vp_change'), 
#                north+shift_north, east+shift_east, z, 
#                cellData={'Vp':model_vel})    
