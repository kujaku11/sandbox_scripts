# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 14:42:50 2014

@author: jpeacock
"""

import numpy as np
from evtk.hl import gridToVTK, pointsToVTK
import os
import simplekml as skml

#vfn = r"/mnt/hgfs/jpeacock/Documents/ParaviewFiles/Teleseismic/lvm5sav.ascii"
#sfn = r"/mnt/hgfs/jpeacock/Documents/ParaviewFiles/Teleseismic/model.desc"
vfn = r"c:\Users\jpeacock\Documents\ParaviewFiles\Teleseismic\lvm5sav.ascii"
sfn = r"c:\Users\jpeacock\Documents\ParaviewFiles\Teleseismic\model.desc"

grid_center = np.array((335358.9, 4170177))
#mt_center = np.array((331816, 4194908)) # mono basin center
mt_center = np.array((336800., 4167525.)) # long valley center
cell_size = (2, 2, 2)

grid_shift = (grid_center-mt_center)/1000.
#grid_shift = np.array([0, 0])

vel_arr = np.loadtxt(vfn, delimiter=' ', dtype=[('east', np.float),
                                                ('north', np.float),
                                                ('z', np.float),
                                                ('vel', np.float)])


#set depth to be positive downwards
vel_arr['z'] *= -1

#need to make a simple grid in each direction
#VTK needs the grid to n+1 larger than the data 
east = np.arange(vel_arr['east'].min(), vel_arr['east'].max()+2*cell_size[0],
                 cell_size[0])
north = np.arange(vel_arr['north'].min(), vel_arr['north'].max()+2*cell_size[1],
                  cell_size[1])
z = np.arange(vel_arr['z'].min(), vel_arr['z'].max()+2*cell_size[2],
              cell_size[2])

#create dictionaries to get the indexes correct for putting it in 
# a right hand coordinate system with Z + down              
east_index_dict = dict([(xkey, xvalue) for xvalue, xkey in enumerate(east)])
north_index_dict = dict([(ykey, yvalue) for yvalue, ykey in enumerate(north)])
z_index_dict = dict([(zkey, zvalue) for zvalue, zkey in enumerate(z)])

n_east = east.shape[0]-1
n_north = north.shape[0]-1
n_z = z.shape[0]-1

model_vel = np.zeros((n_north, n_east, n_z))

for v_arr in vel_arr:
    e_index = east_index_dict[v_arr['east']]
    n_index = north_index_dict[v_arr['north']]
    z_index = z_index_dict[v_arr['z']]
    model_vel[n_index, e_index, z_index] = np.nan_to_num(v_arr['vel'])

#vel.reshape()
gridToVTK(os.path.join(r"c:\Users\jpeacock\Documents\LV\lv_3d_models", 
                       'dawson_teleseismic_vp_lvc16'), 
          north-grid_shift[0], 
          east-grid_shift[1],
          z, 
          cellData={'Vp':model_vel})
          
          
station_loc = np.loadtxt(sfn, skiprows=6,
                         dtype=[('lat', np.float),
                                 ('lon', np.float),
                                 ('north', np.float),
                                 ('east', np.float),
                                 ('rel_north', np.float),
                                 ('rel_east', np.float), 
                                 ('elev', np.float)])

pointsToVTK(os.path.join(r"c:\Users\jpeacock\Documents\LV\lv_3d_models",
                         'dawson_teleseismic_loc_lvc16'),
            station_loc['rel_east'].copy()-grid_shift[0],
            station_loc['rel_north'].copy()-grid_shift[1],
            station_loc['elev'].copy()/1000,
            data={'elev':station_loc['elev'].copy()/1000})
            
#kml_obj = skml.Kml()
#for s_arr in station_loc:
#    kml_obj.newpoint(coords=[(-s_arr['lon'], s_arr['lat'], s_arr['elev'])])
#    
#kml_obj.save(os.path.join(os.path.dirname(vfn), 'dawson_teleseismic_stations.kml'))

    
