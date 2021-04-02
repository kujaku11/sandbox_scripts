# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 14:03:32 2019

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from mtpy.modeling import modem
from mtpy.utils import gis_tools
from mtpy.utils import array2raster
from pyevtk.hl import pointsToVTK

# =============================================================================
# Inputs
# =============================================================================
fn = r"c:\Users\jpeacock\Documents\MountainPass\zzthick-190211-neg.axyz"
d = 50.0
utm_zone = "11N"
data_epsg = 26911
model_center = (35.488658, -115.494148)

dfn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_07\mp_modem_data_z03_topo_edit.dat"

if dfn is not None:
    d_obj = modem.Data()
    d_obj.read_data_file(dfn)

# =============================================================================
# Load in file
# =============================================================================
a = np.loadtxt(fn, skiprows=3, dtype=np.float, delimiter=None).T

### compute the lower left hand corner of the raster
lower_left = gis_tools.project_point_utm2ll(a[1].min(), a[0].min(), utm_zone)
lower_left = (a[1].min(), a[0].min())

east, north, zone = gis_tools.project_points_ll2utm(a[1], a[0], datum="NAD27")

### make equally spaced points on regular grid
x_new = np.linspace(east.min(), east.max(), num=(east.max() - east.min()) / d)
y_new = np.linspace(north.min(), north.max(), num=(north.max() - north.min()) / d)

xg, yg = np.meshgrid(x_new, y_new)

### interpolate the data onto a regular grid
basement = interpolate.griddata((east, north), -1 * a[2], (xg, yg), method="cubic")

### make raster
b = array2raster.array2raster(
    fn[:-4] + ".tif", (lower_left[1], lower_left[0]), d, d, basement
)


### make a point cloud
x0, y0, z0 = gis_tools.project_point_ll2utm(
    model_center[0], model_center[1], epsg=data_epsg
)
x = (north.copy() - y0) / 1000.0
y = (east.copy() - x0) / 1000.0
z = -1 * a[2].copy()
pointsToVTK(fn[0:-4], x, y, z, {"depth": z})

fig = plt.figure(2)
fig.clf()

ax = fig.add_subplot(1, 1, 1, aspect="equal")
im = ax.pcolormesh(xg, yg, basement, cmap="viridis", vmin=0, vmax=3.00)
plt.colorbar(mappable=im, ax=ax)

if dfn is not None:
    for lat, lon in zip(d_obj.station_locations.lat, d_obj.station_locations.lon):
        s_east, s_north, s_zone = gis_tools.project_point_ll2utm(
            lat, lon, epsg=data_epsg
        )
        ax.scatter(s_east, s_north, marker="v", c="k", s=15)


plt.show()
