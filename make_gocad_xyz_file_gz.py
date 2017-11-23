# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 13:32:40 2017

@author: jpeacock
"""

import mtpy.modeling.modem_model as modem
import mtpy.utils.gis_tools as gis_tools
import numpy as np

mfn = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03\gz_err03_cov02_NLCG_057.rho"
model_center = (38.831979,  -122.828190)

model_center_proj = gis_tools.project_point_ll2utm(model_center[0],
                                                   model_center[1],
                                                   epsg=26742)

m_obj = modem.Model()
m_obj.read_model_file(mfn)

clip = 6

m_to_feet = 3.280839895

# need to center the location, which is in the nodes
east = m_obj.nodes_east[clip:-clip]*m_to_feet
north = m_obj.nodes_north[clip:-clip]*m_to_feet
z = m_obj.nodes_z[0:-clip]*m_to_feet
res = m_obj.res_model[clip:-clip,
                      clip:-clip,
                      0:-clip]

east = np.array([east[0:ii].sum() for ii in range(east.size)])
north = np.array([north[0:ii].sum() for ii in range(north.size)])
z = np.array([z[0:ii].sum() for ii in range(z.size)])

east -= east.max()/2
north -= north.max()/2

# Need to shift into projected coordinates
east += model_center_proj[0]
north += model_center_proj[1]
z -= 1260

lines = ['# USGS MT RESISTIVITY MODEL',
         '# Author = J. Peacock',
         '# Date = 2017-11-21',
         '# Location = Geysers, CA',
         '# Coordinate System = NAD27 / California 402 State Plane Zone 2 ',
         '# Spatial Units = feet',
         '# Data Units = Ohm-m',
         '# Data Type = Electrical Resistivity',
         '# Depth = Positive Down',
         '# *** Data ***',
         '# Easting, Northing, Depth, Resistivity']
for kk, zz in enumerate(z):
    for ii, xx in enumerate(east):
        for jj, yy in enumerate(north):
            line = '{0:.4f} {1:.4f} {2:+.4f} {3:.4f}'.format(xx, yy, zz,
                                                               res[jj, ii, kk])
            lines.append(line)

with open(r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\mt_model_proj.txt", 'w') as fid:
    fid.write('\n'.join(lines))
    