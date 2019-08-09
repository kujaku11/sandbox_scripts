# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 14:54:24 2019

@author: jpeacock
"""

import pandas as pd
import numpy as np
from mtpy.modeling import modem
from scipy import interpolate

m_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\gz_z03_c02_074.rho"
fn_felsite = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\Top_Felsite_Points_WGS84_mc.csv"

df_felsite = pd.read_csv(fn_felsite)

for col in df_felsite.columns:
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

felsite = m_obj.res_model.copy()
for x_index, xx in enumerate(m_obj.grid_north):
    for y_index, yy in enumerate(m_obj.grid_east):
        f_depth = f_map[y_index, x_index]
        if np.isnan(f_depth):
            continue
            #f_depth = np.nanmax(f_map)
        z_index = np.where(m_obj.grid_z <= f_depth)
        try:
            felsite[x_index, y_index, z_index] = 1E12
        except IndexError:
            pass
    
    
felsite[np.where(m_obj.res_model > 1E11)] = 1E12

m_obj.res_model = felsite
m_obj.write_vtk_file(vtk_fn_basename='geysers_felsite_inv06')
m_obj.write_model_file(model_fn_basename='gz_felsite_inv06.rho')


    



