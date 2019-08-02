# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 14:54:24 2019

@author: jpeacock
"""

import pandas as pd
import numpy as np
from mtpy.modeling import modem
from scipy import interpolate

m_fn = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03\gz_err03_cov02_NLCG_057.rho"
fn_steam = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\tos_points_mc.csv"
fn_felsite = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\Top_Felsite_Points_WGS84_mc.csv"

df_steam = pd.read_csv(fn_steam)
df_felsite = pd.read_csv(fn_felsite)

for col in df_steam.columns:
    df_steam[col] *= 1000
    df_felsite[col] *= 1000

m_obj = modem.Model()
m_obj.read_model_file(m_fn)

### first need to interpolate depth data onto a similar map
grid_north, grid_east = np.meshgrid(m_obj.grid_north, m_obj.grid_east)

#--> felsite
f_points = np.array([df_felsite.northing, df_felsite.easting]).T
f_map = interpolate.griddata(f_points, df_felsite.depth,
                             (grid_north, grid_east),
                             method='cubic')
#--> steam
s_points = np.array([df_steam.northing, df_steam.easting]).T
s_map = interpolate.griddata(s_points, df_steam.depth,
                             (grid_north, grid_east),
                             method='cubic')
s_map[np.where(s_map < 0)] = 0
s_map[np.where(s_map > 2300)] = 2300
#s_map[12:26, 26:41] = 


steam = m_obj.res_model.copy()
steam[:, :, :] = 1E12
for x_index, xx in enumerate(m_obj.grid_north):
    for y_index, yy in enumerate(m_obj.grid_east):
        s_depth = s_map[y_index, x_index]
        if np.isnan(s_depth):
            continue
        else:
            f_depth = f_map[y_index, x_index]
            if np.isnan(f_depth):
                f_depth = 3000
            z_index = np.where((m_obj.grid_z <= f_depth) & 
                               (m_obj.grid_z >= s_depth))
            steam[x_index, y_index, z_index] = m_obj.res_model[x_index, 
                                                               y_index, 
                                                               z_index]
            
    
    
steam[np.where(m_obj.res_model > 1E11)] = 1E12

m_obj.res_model = steam
m_obj.write_vtk_file(vtk_fn_basename='geysers_steam_res')


    



