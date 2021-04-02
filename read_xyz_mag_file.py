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
fn = r"g:\GabbsValley\DataRelease_PFA\Mag\Databases\GV_mag.csv"
d = 50.0
utm_zone = "11N"
data_epsg = 26911
model_center = (38.774109, -118.151242)

dfn = r"c:\Users\jpeacock\Documents\Geothermal\GraniteSprings\modem_inv\inv_01\gs_modem_data_err03_tip02.dat"

if dfn is not None:
    d_obj = modem.Data()
    d_obj.read_data_file(dfn)

# =============================================================================
# Load in file
# =============================================================================
a = np.loadtxt(
    fn,
    dtype={
        "names": ("lon", "lat", "easting", "northing", "elev", "mag", "time", "date"),
        "formats": (
            np.float,
            np.float,
            np.float,
            np.float,
            np.float,
            np.float,
            np.str,
            np.str,
        ),
    },
    skiprows=3,
    delimiter=",",
).T

### compute the lower left hand corner of the raster
lower_left = (a["lon"].min(), a["lat"].min())

### make equally spaced points on regular grid
x_new = np.linspace(
    a["easting"].min(),
    a["easting"].max(),
    num=(a["easting"].max() - a["easting"].min()) / d,
)
y_new = np.linspace(
    a["northing"].min(),
    a["northing"].max(),
    num=(a["northing"].max() - a["northing"].min()) / d,
)

xg, yg = np.meshgrid(x_new, y_new)

### interpolate the data onto a regular grid
basement = interpolate.griddata(
    (a["easting"], a["northing"]), a["mag"], (xg, yg), method="linear"
)

### make raster
b = array2raster.array2raster(
    fn[:-4] + ".tif", lower_left, d, d, basement, projection="NAD83"
)

### make a point cloud
x0, y0, z0 = gis_tools.project_point_ll2utm(
    model_center[0], model_center[1], epsg=data_epsg
)
x = (a["northing"].copy() - y0) / 1000.0
y = (a["easting"].copy() - x0) / 1000.0
z = a["mag"].copy() / np.abs(a["mag"]).max()
pointsToVTK(fn[0:-4], x, y, z, {"mag": z})

fig = plt.figure(1)
fig.clf()

ax = fig.add_subplot(1, 1, 1, aspect="equal")
im = ax.pcolormesh(xg, yg, basement, cmap="viridis")
plt.colorbar(mappable=im, ax=ax)

if dfn is not None:
    for lat, lon in zip(d_obj.station_locations.lat, d_obj.station_locations.lon):
        east, north, zone = gis_tools.project_point_ll2utm(lat, lon, epsg=data_epsg)
        ax.scatter(east, north, marker="v", c="k", s=15)


plt.show()
