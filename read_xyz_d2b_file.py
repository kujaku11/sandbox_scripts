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
fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Battle_Mountain\GIS\potential_fields\D2B_files_for_UNR\Depth_to_Basement_Surface.xyz"
d = 50.0
utm_zone = "11N"
data_epsg = 26911
model_center = (40.532514, -116.826831)

dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Battle_Mountain\modem_inv\inv_04\bm_modem_data_z03_t02_02.dat"

if dfn is not None:
    d_obj = modem.Data()
    d_obj.read_data_file(dfn)

# =============================================================================
# Load in file
# =============================================================================
a = np.loadtxt(fn, skiprows=3, dtype=np.float, delimiter=None).T

### compute the lower left hand corner of the raster
lower_left = gis_tools.project_point_utm2ll(a[0].min(), a[1].min(), utm_zone)

### make equally spaced points on regular grid
x_new = np.linspace(
    a[0].min(), a[0].max(), num=int((a[0].max() - a[0].min()) / d)
)
y_new = np.linspace(
    a[1].min(), a[1].max(), num=int((a[1].max() - a[1].min()) / d)
)

xg, yg = np.meshgrid(x_new, y_new)

### interpolate the data onto a regular grid
basement = interpolate.griddata((a[0], a[1]), a[2], (xg, yg), method="cubic")

### make raster
b = array2raster.array2raster(
    fn[:-4] + ".tif", (lower_left[1], lower_left[0]), d, d, basement
)


### make a point cloud
x0, y0, z0 = gis_tools.project_point_ll2utm(
    model_center[0], model_center[1], epsg=data_epsg
)
x = (a[1].copy() - y0) / 1000.0
y = (a[0].copy() - x0) / 1000.0
z = -1 * a[2].copy() / 1000.0
pointsToVTK(fn[0:-4], x, y, z, {"depth": z})

fig = plt.figure(2)
fig.clf()

ax = fig.add_subplot(1, 1, 1, aspect="equal")
im = ax.pcolormesh(xg, yg, basement / 1000.0, cmap="viridis", vmin=-3, vmax=3)
plt.colorbar(mappable=im, ax=ax)

if dfn is not None:
    for lat, lon in zip(
        d_obj.station_locations.lat, d_obj.station_locations.lon
    ):
        east, north, zone = gis_tools.project_point_ll2utm(
            lat, lon, epsg=data_epsg
        )
        ax.scatter(east, north, marker="v", c="k", s=15)


plt.show()
