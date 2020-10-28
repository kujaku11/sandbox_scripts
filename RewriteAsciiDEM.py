# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 13:50:55 2014

@author: jpeacock-pr
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.interpolate as spi

dirpath = r"C:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\ASTER"
dem_ascii = os.path.join(dirpath, r"mb_crop_survey_area.asc")


dfid = file(dem_ascii, "r")
d_dict = {}
for ii in range(6):
    dline = dfid.readline()
    dline = dline.strip().split()
    key = dline[0].strip().lower()
    value = float(dline[1].strip())
    d_dict[key] = value

x0 = d_dict["xllcorner"]
y0 = d_dict["yllcorner"]
nx = int(d_dict["ncols"])
ny = int(d_dict["nrows"])
cs = d_dict["cellsize"]
new_cs = 200
rs = 6

easting = np.arange(x0, x0 + cs * (nx), cs)
northing = np.arange(y0, y0 + cs * (ny), cs)

east_mesh, north_mesh = np.meshgrid(easting, northing, indexing="ij")

elevation = np.zeros((nx, ny))

for ii in range(1, int(ny) + 2):
    dline = dfid.readline()
    if len(str(dline)) > 1:
        # needs to be backwards because first line is the furthest north row.
        elevation[:, -ii] = np.array(dline.strip().split(" "), dtype="float")
    else:
        break

dfid.close()

# resample the data accordingly
new_east = easting[np.arange(0, easting.shape[0], rs)]
new_north = northing[np.arange(0, northing.shape[0], rs)]
new_x, new_y = np.meshgrid(
    np.arange(0, easting.shape[0], rs), np.arange(0, northing.shape[0], rs)
)
new_elev = elevation[new_x, new_y]

##interpolate onto a larger grid to make the file size a little smaller
# elev_func = spi.interp2d(easting, northing, elevation, kind='cubic')
#
#
# new_east = np.arange(easting.min(), easting.max()+new_cs, new_cs)
# new_north = np.arange(northing.min(), northing.max()+new_cs, new_cs)
#
# new_elev = elev_func(new_east, new_north)

new_east_mesh, new_north_mesh = np.meshgrid(new_east, new_north, indexing="ij")
# plot the elevation to be sure its all correct
fig = plt.figure(1,)
ax = fig.add_subplot(1, 1, 1, aspect="equal")
# pm = ax.pcolormesh(east_mesh, north_mesh, elevation, cmap='summer',
#                   vmin=elevation.min())
# pm = ax.pcolormesh(new_east_mesh, new_north_mesh, new_elev, cmap='summer',
#                   vmin=elevation.min(), vmax=elevation.max())
pm = ax.pcolormesh(new_elev, cmap="summer", vmin=elevation.min(), vmax=elevation.max())
plt.show()

# ==============================================================================
# write ascii file as x, y, z
# ==============================================================================
asc_fn = os.path.join(dirpath, "Survey_Elevation.asc")
alines = ["{0:^15}{1:^15}{2:^15}\n".format("easting(m)", "northing(m)", "elevation(m)")]
for ii, east in enumerate(new_east):
    for jj, north in enumerate(new_north):
        aline = "{0:^15.1f}{1:^15.1f}{2:^15.1f}\n".format(east, north, new_elev[jj, ii])
        alines.append(aline)
afid = file(asc_fn, "w")
afid.writelines(alines)
afid.close()
