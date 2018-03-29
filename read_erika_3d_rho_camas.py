# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:14:12 2018

@author: jpeacock
"""

import os
import numpy as np
from evtk.hl import gridToVTK
import mtpy.utils.gis_tools as gis_tools

# =============================================================================
# parameters
# =============================================================================
rho_fn = r"C:\Users\jpeacock\Documents\Geothermal\Camas\camas_rho.dat"

# =============================================================================
# read in file
# =============================================================================
rho_arr = np.loadtxt(rho_fn, skiprows=1, delimiter=' ',
                     dtype={'names':('east', 'north', 'elev', 'res', 'log10_res'),
                            'formats':(np.float, np.float, np.float, np.float, np.float)})

east = np.array(sorted(list(set(rho_arr['east']))))
north = np.array(sorted(list(set(rho_arr['north']))))
z = np.array(sorted(list(set(rho_arr['elev']))))

res = np.zeros((north.size, east.size, z.size))

for r_arr in rho_arr:
    n_index = np.where(north == r_arr['north'])[0][0]
    e_index = np.where(east == r_arr['east'])[0][0]
    z_index = np.where(z == r_arr['elev'])[0][0]
    
    res[n_index, e_index, z_index] = r_arr['res']