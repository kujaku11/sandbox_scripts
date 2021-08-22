# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 13:28:04 2018

@author: jpeacock
"""

import mtpy.utils.filehandling as mtfh
import numpy as np
import scipy.interpolate as interpolate

import matplotlib.pyplot as plt

# =============================================================================
# Inputs
# =============================================================================
fn = r"c:\Users\jpeacock\Documents\SaudiArabia\GIS\etopo1.asc"

rotation_angle = 30.0

# =============================================================================
# load in file
# =============================================================================
x, y, values = mtfh.read_surface_ascii(fn)

# =============================================================================
# Interpolate x and y to make sure they have the same number of points
# =============================================================================
n = int(np.mean([x.size, y.size]))
xi = np.linspace(x.min(), x.max(), n)
yi = np.linspace(y.min(), y.max(), n)

grid_xi, grid_yi = np.meshgrid(xi, yi)

x_points, y_points = np.broadcast_arrays(x[None, :], y[:, None])
points = np.array([x_points.ravel(), y_points.ravel()]).T
vi = interpolate.griddata(points, values.ravel(), (grid_xi, grid_yi), method="linear")

# =============================================================================
# rotate grid
# =============================================================================
cos_ang = np.cos(np.deg2rad(rotation_angle))
sin_ang = np.sin(np.deg2rad(rotation_angle))
rot_matrix = np.matrix(np.array([[cos_ang, sin_ang], [-sin_ang, cos_ang]]))


rot_xy = np.array(np.dot(rot_matrix, np.array([xi, yi])))
xr = rot_xy[0].copy()
yr = rot_xy[1].copy()

xr -= xr.mean() - xi.mean()
yr -= yr.mean() - yi.mean()

rot_x, rot_y = np.meshgrid(xr, yr)

fig = plt.figure()
fig.clf()

ax1 = fig.add_subplot(1, 3, 1, aspect="equal")
im1 = ax1.pcolormesh(x_points, y_points, values)

ax2 = fig.add_subplot(1, 3, 2, aspect="equal", sharex=ax1, sharey=ax1)
im2 = ax2.pcolormesh(grid_xi, grid_yi, vi)
#
ax2 = fig.add_subplot(1, 3, 3, aspect="equal", sharex=ax1, sharey=ax1)
im2 = ax2.pcolormesh(rot_x, rot_y, vi)


# ax1 = fig.add_subplot(1, 1, 1, aspect='equal')
# ax1.scatter(xi, yi, marker='v', c='b')
# ax1.scatter(xr, yr, marker='s', c='r')

plt.show()
