# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 16:38:19 2017

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt


def get_padding_cells(cell_width, max_distance, num_cells):
    scaling = ((max_distance) / (cell_width * 1.2)) ** (1.0 / (num_cells - 1))
    print scaling

    padding = np.zeros(num_cells)
    for ii in range(num_cells):
        exp_pad = np.round((cell_width * 1.2) * scaling ** ii, -2)
        mult_pad = np.round(
            (cell_width * 1.2) * ((1 - 1.2 ** (ii + 1)) / (1 - 1.2)), -2
        )
        padding[ii] = max([exp_pad, mult_pad])

        print exp_pad, mult_pad
    return padding


west = -10000
east = 10000
north = 10000
south = -10000

east_west_ext = 300000
north_south_ext = 300000
z_ext = 300000

cell_size_east = 500
cell_size_north = 500

pad_east = 18
pad_north = 18

pad_cell_num = 4

##---> make station mesh
# get station padding cells
pad_width_east = 1.5 * cell_size_east * pad_cell_num
pad_width_north = 1.5 * cell_size_north * pad_cell_num

station_west = west - pad_width_east
station_east = east + pad_width_east
station_south = south - pad_width_north
station_north = north + pad_width_north


inner_east = np.arange(station_west, station_east + cell_size_east, cell_size_east)
inner_north = np.arange(station_south, station_north + cell_size_north, cell_size_north)

## get outside station area padding cells

padding_east = get_padding_cells(
    cell_size_east, east_west_ext / 2 - station_east, pad_east
)
padding_north = get_padding_cells(
    cell_size_north, north_south_ext / 2 - station_north, pad_north
)


grid_east = np.append(
    np.append(-1 * padding_east[::-1] + station_west, inner_east),
    padding_east + station_east,
)
grid_north = np.append(
    np.append(-1 * padding_north[::-1] + station_south, inner_north),
    padding_north + station_north,
)


m = np.logspace(
    np.log10(10),
    np.log10(50000 - np.logspace(np.log10(10), np.log10(50000), num=30)[-2]),
    num=30 - 5,
)


fig = plt.figure()
plt.clf()

# make a rotation matrix to rotate data
# cos_ang = np.cos(np.deg2rad(mesh_rotation_angle))
# sin_ang = np.sin(np.deg2rad(mesh_rotation_angle))

# turns out ModEM has not accomodated rotation of the grid, so for
# now we will not rotate anything.
cos_ang = 1
sin_ang = 0

# --->plot map view
ax1 = fig.add_subplot(1, 1, 1, aspect="equal")


east_line_xlist = []
east_line_ylist = []
north_min = grid_north.min()
north_max = grid_north.max()
for xx in grid_east:
    east_line_xlist.extend(
        [xx * cos_ang + north_min * sin_ang, xx * cos_ang + north_max * sin_ang]
    )
    east_line_xlist.append(None)
    east_line_ylist.extend(
        [-xx * sin_ang + north_min * cos_ang, -xx * sin_ang + north_max * cos_ang]
    )
    east_line_ylist.append(None)
ax1.plot(east_line_xlist, east_line_ylist, lw=1, color="k")

north_line_xlist = []
north_line_ylist = []
east_max = grid_east.max()
east_min = grid_east.min()
for yy in grid_north:
    north_line_xlist.extend(
        [east_min * cos_ang + yy * sin_ang, east_max * cos_ang + yy * sin_ang]
    )
    north_line_xlist.append(None)
    north_line_ylist.extend(
        [-east_min * sin_ang + yy * cos_ang, -east_max * sin_ang + yy * cos_ang]
    )
    north_line_ylist.append(None)
ax1.plot(north_line_xlist, north_line_ylist, lw=1, color="k")

# if east_limits == None:
#    ax1.set_xlim(plot_east.min()-10*cell_size_east,
#                 plot_east.max()+10*cell_size_east)
# else:
#    ax1.set_xlim(east_limits)
#
# if north_limits == None:
#    ax1.set_ylim(plot_north.min()-10*cell_size_north,
#                 plot_north.max()+ 10*cell_size_east)
# else:
#    ax1.set_ylim(north_limits)

ax1.set_ylabel("Northing (m)", fontdict={"size": 9, "weight": "bold"})
ax1.set_xlabel("Easting (m)", fontdict={"size": 9, "weight": "bold"})

plt.show()
