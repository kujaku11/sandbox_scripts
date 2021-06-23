# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 09:37:02 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""

import numpy as np
import pandas as pd
from mtpy.modeling import modem
from mtpy.utils import gis_tools
from scipy import interpolate
from mtpy.utils import array2raster

# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_06\um_z05_c025_089.rho"
# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_09\um_z05_c05_089.rho"
mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_09\um_z05_c025_086.rho"

surface_fn = r"c:\Users\jpeacock\OneDrive - DOI\General - Umatilla\2&3D modeling\exported_3D_surfaces\for_Jared\csvFiles\dem_toPts2.csv"
prebase_fn = r"c:\Users\jpeacock\OneDrive - DOI\General - Umatilla\2&3D modeling\exported_3D_surfaces\for_Jared\csvFiles\preBase_toPts2.csv"
precrb_fn = r"c:\Users\jpeacock\OneDrive - DOI\General - Umatilla\2&3D modeling\exported_3D_surfaces\for_Jared\csvFiles\preCRB_toPts2.csv"

model_center = (45.654713, -118.547148)
# model_center = (45.650594, -118.562997)

m_epsg = 26911
m_east, m_north, m_zone = gis_tools.project_point_ll2utm(model_center[0], 
                                                         model_center[1],
                                                         epsg=m_epsg)


def interp(model_east, model_north, surface_east, surface_north, surface_values):
    xg, yg = np.meshgrid(surface_east, surface_north)
    mxg, myg = np.meshgrid(model_east, model_north)
    points = np.vstack([arr.flatten() for arr in [xg, yg]]).T
    values = surface_values.flatten()
    xi = np.vstack([arr.flatten() for arr in [mxg, myg]]).T

    return interpolate.griddata(points, values, xi).reshape(mxg.shape)

def read(fn):
    df = pd.read_csv(fn, header=0, index_col=0)
    x = df.x83utm11.unique()
    y = df.y83utm11.unique()
    z = df.grid_code.to_numpy()
    z = -1 * z.reshape((y.size, x.size))
    
    return x, y, z


m = modem.Model()
m.read_model_file(mfn)
mx = m.grid_east + m_east
my = m.grid_north + m_north

x, y, dem = read(surface_fn)
x, y, base = read(prebase_fn)
x, y, crb = read(precrb_fn)

mdem = interp(mx[:-1], my[:-1], x, y, dem)
mbase = interp(mx[:-1], my[:-1], x, y, base)
mcrb = interp(mx[:-1], my[:-1], x, y, crb)

c_top = np.zeros_like(mdem)
c_crb = np.zeros_like(mdem)
c_base = np.zeros_like(mdem)
c_8k = np.zeros_like(mdem)
c_15k = np.zeros_like(mdem)

for ii in range(mx.size - 1):
    for jj in range(my.size - 1):
        if np.nan_to_num(mcrb[jj, ii]) == 0:
            continue
        k1 = 0
        k2 = np.where(m.grid_z >= mcrb[jj, ii])[0][0]
        c = (1./m.res_model[jj, ii, k1:k2]) * abs(m.grid_z[k1:k2])
        c_top[jj, ii] = np.nansum(c)
        
        k1 = np.where(m.grid_z >= mcrb[jj, ii])[0][0]
        k2 = np.where(m.grid_z >= mbase[jj, ii])[0][0]
        c = (1./m.res_model[jj, ii, k1:k2]) * abs(m.grid_z[k1:k2])
        c_crb[jj, ii] = np.nansum(c)
        
        k1 = np.where(m.grid_z >= mbase[jj, ii])[0][0]
        k2 = np.where(m.grid_z >= mbase[jj, ii] + 3000)[0][0]
        c = (1./m.res_model[jj, ii, k1:k2]) * abs(m.grid_z[k1:k2])
        c_base[jj, ii] = np.nansum(c)
        
        k1 = np.where(m.grid_z >= 6000)[0][0]
        k2 = np.where(m.grid_z >= 10000)[0][0]
        c = (1./m.res_model[jj, ii, k1:k2]) * abs(m.grid_z[k1:k2])
        c_8k[jj, ii] = np.nansum(c)
        
        k1 = np.where(m.grid_z >= 10000)[0][0]
        k2 = np.where(m.grid_z >= 15000)[0][0]
        c = (1./m.res_model[jj, ii, k1:k2]) * abs(m.grid_z[k1:k2])
        c_15k[jj, ii] = np.nansum(c)
        
        
m2r = array2raster.ModEM_to_Raster()
ll_cc = m2r.get_model_lower_left_coord(m,
    model_center=model_center, pad_east=9, pad_north=9
)
m2r.model_obj = m

m2r.lower_left_corner = ll_cc
m2r.save_path = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_09\depth_slices"
m2r.projection = "NAD83"

for ii, carray in enumerate([c_top, c_crb, c_base, c_8k, c_15k]):
    m2r.model_obj.grid_z = np.array([ii, 100])
    m2r.model_obj.res_model = carray.reshape((mdem.shape[0], mdem.shape[1], 1))
    m2r.write_raster_files()




        
        
        


