# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 16:47:38 2017

@author: jpeacock
"""

import numpy as np
from evtk.hl import gridToVTK


mesh_fn = (
    r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\AMP_EffSusc_lp_NoPad.mesh"
)
sus_fn = (
    r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\AMP_EffSusc_lp_NoPad.sus"
)
mb_east, mb_north = (596550.0, 5397110.0)


with open(mesh_fn, "r") as fid:
    mesh_lines = fid.readlines()

ne, nn, nz = [int(ii.strip()) for ii in mesh_lines[0].split()]
east, north, elev = [float(ii.strip()) for ii in mesh_lines[1].split()]

east_nodes = np.array([float(ii.strip()) for ii in mesh_lines[2].split()])
north_nodes = np.array([float(ii.strip()) for ii in mesh_lines[3].split()])
z_nodes = np.array([float(ii.strip()) for ii in mesh_lines[4].split()])

# get the actuall locations
grid_east = np.append([0], east_nodes)
grid_north = np.append([0], north_nodes)
grid_z = np.append([0], z_nodes)

grid_east = (
    np.array([grid_east[0 : ii + 1].sum() for ii in range(grid_east.size)]) / 1000.0
)
grid_north = (
    np.array([grid_north[0 : ii + 1].sum() for ii in range(grid_north.size)]) / 1000.0
)
grid_z = np.array([grid_z[0 : ii + 1].sum() for ii in range(grid_z.size)]) / 1000.0

grid_diff_east = (mb_east - east) / 1000.0
grid_diff_north = (mb_north - north) / 1000.0

grid_east -= grid_diff_east
grid_north -= grid_diff_north


sus_array = np.zeros(ne * nn * nz)

with open(sus_fn, "r") as fid:
    sus_lines = fid.readlines()

for ii, s_line in enumerate(sus_lines):
    try:
        value = float(s_line.strip())
        sus_array[ii] = value
    except ValueError:
        break

sus_array = sus_array.reshape((nn, ne, nz))

gridToVTK(
    r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\mag_suscept",
    grid_north,
    grid_east,
    grid_z,
    cellData={"Susceptibility": sus_array},
)
