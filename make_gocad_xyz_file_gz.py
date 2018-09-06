# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 13:32:40 2017

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import mtpy.utils.gis_tools as gis_tools
import numpy as np
import matplotlib.pyplot as plt

mfn = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03\gz_err03_cov02_NLCG_057.rho"
dfn = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03\gz_data_err03_tec_edit.dat"
model_center = (38.831979,  -122.828190)


model_center_proj = gis_tools.project_point_ll2utm(model_center[0],
                                                   model_center[1],
                                                   epsg=26742)

m_obj = modem.Model()
m_obj.read_model_file(mfn)

clip = 6

m_to_feet = 3.280839895

# need to center the location, which is in the nodes
east = m_obj.nodes_east[clip:-clip+1]*m_to_feet
north = m_obj.nodes_north[clip:-clip+1]*m_to_feet
z = m_obj.nodes_z[0:-clip]*m_to_feet
res = m_obj.res_model[clip:-clip+1,
                      clip:-clip+1,
                      0:-clip+1]

east = np.array([east[0:ii].sum() for ii in range(east.size)])
north = np.array([north[0:ii].sum() for ii in range(north.size)])
z = np.array([z[0:ii].sum() for ii in range(z.size)])

east -= east.max()/2
north -= north.max()/2

# Need to shift into projected coordinates
east += model_center_proj[0]
north += model_center_proj[1]
z -= (1260*m_to_feet)

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
    
# plot to make sure
    
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

d = modem.Data()
d.read_data_file(dfn)

plot_x, plot_y = np.meshgrid(east, north)

im = plt.pcolormesh(plot_x, plot_y, np.log10(res[:, :, 53]),
                     vmin=0, vmax=np.log10(300), cmap='jet_r')
plt.colorbar(im, ax=ax)

proj_d = gis_tools.project_point_ll2utm(d.station_locations.lat,
                                        d.station_locations.lon,
                                        epsg=26742)
plt.scatter(proj_d.easting, 
            proj_d.northing,
            marker='v',
            c='k',
            s=25)

plt.show()
    
# write out station locations
d_lines = ['# USGS MT STATION LOCATIONS',
           '# Author = J. Peacock',
           '# Date = 2017-11-21',
           '# Location = Geysers, CA',
           '# Coordinate System = NAD27 / California 402 State Plane Zone 2 ',
           '# Spatial Units = feet',
           '# Data Type = Electrical Resistivity',
           '# Depth = Positive Down',
           '# *** Data ***',
           '# Easting, Northing, Elevation']
for ee, nn, zz in zip(proj_d.easting, proj_d.northing, d.station_locations.elev):
    d_lines.append('{0:.2f},{1:.2f},{2:.2f}'.format(ee, nn, (zz)*m_to_feet))
    
with open(r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\mt_stations.txt", 'w') as fid:
    fid.write('\n'.join(d_lines))