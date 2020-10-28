# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 11:15:04 2015

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt

eq_fn = r"C:\Users\jpeacock\Documents\MountainPass\southern_california_earthquake_locations.txt"

lon_max = -115.0
lon_min = -116.0
lat_min = 35.0
lat_max = 36.0

data_type = {
    "names": (
        "year",
        "month",
        "day",
        "hour",
        "minute",
        "seconds",
        "lat",
        "lon",
        "depth",
        "mag",
    ),
    "formats": (
        np.int,
        np.int,
        np.int,
        np.int,
        np.int,
        np.float,
        np.float,
        np.float,
        np.float,
        np.float,
    ),
}

cols = range(12)
cols.remove(6)

eq_arr = np.loadtxt(eq_fn, dtype=data_type, usecols=cols)

crop_eq_arr = eq_arr[np.where((eq_arr["lat"] >= lat_min) & (eq_arr["lat"] <= lat_max))]
crop_eq_arr = crop_eq_arr[
    np.where((crop_eq_arr["lon"] >= lon_min) & (crop_eq_arr["lon"] <= lon_max))
]

fig = plt.figure(1)
ax = fig.add_subplot(1, 1, 1, aspect="equal")
ax.scatter(crop_eq_arr["lon"], crop_eq_arr["lat"], s=2, marker="o")
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)
plt.show()

save_fn = "{0}_crop.txt".format(eq_fn[:-4])
np.savetxt(
    save_fn,
    crop_eq_arr,
    fmt=[
        "%.0f",
        "%.0f",
        "%.0f",
        "%.0f",
        "%.0f",
        "%.2f",
        "%.4f",
        "%.4f",
        "%.4f",
        "%.2f",
    ],
    delimiter=",",
    header="year,month,day,hour,minute,seconds,lat,lon,depth,mag",
)
print "wrote crop file to {0}".format(save_fn)

# write a file for arc

arc_arr = np.array(
    [crop_eq_arr["lon"], crop_eq_arr["lat"], crop_eq_arr["depth"], crop_eq_arr["mag"]]
)
save_fn = "{0}_crop_arc.txt".format(eq_fn[:-4])
np.savetxt(save_fn, arc_arr.T, fmt="%.4f", delimiter=",", header="lon,lat,depth,mag")
print "wrote crop file to {0}".format(save_fn)
