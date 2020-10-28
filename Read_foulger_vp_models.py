# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 15:07:00 2015

@author: jpeacock
"""

import os
import numpy as np
import evtk.hl as a2vtk
import mtpy.utils.latlongutmconversion as ll2utm

fn = r"c:\Users\jpeacock\Documents\LV\foulger2003_vp.out"
save_dir = os.path.dirname(fn)

modem_center = (37.699, -118.873)
mt_east = 336800.0
mt_north = 4167510.0

fid = file(fn, "r")
lines = fid.readlines()
fid.close()

# get model origin
origin_str = lines[33]
origin_lines = [float(ii) for ii in origin_str.strip().split()]
v_lat = origin_lines[0] + origin_lines[1] / 60.0
v_lon = -1 * (origin_lines[2] + origin_lines[3] / 60.0)

# --> read station information
station_header = lines[38].strip().split()

station_lines = lines[39:226]


s_dtype = [
    (label, d_type)
    for label, d_type in zip(
        station_header[0:7],
        ["|S5", np.float, np.float, np.float, np.float, np.float, np.float, np.float],
    )
]

station_arr = np.zeros(len(station_lines), dtype=s_dtype)
for ii, sline in enumerate(station_lines):
    s_list = sline.strip().split()[1:]
    s_list = [s_list[0]] + [float(jj) for jj in s_list[1:]]
    station_arr[ii][station_header[0]] = s_list[0]
    station_arr[ii][station_header[1]] = s_list[1] + s_list[2] / 60.0
    station_arr[ii][station_header[2]] = s_list[3] + s_list[4] / 60.0
    station_arr[ii][station_header[3]] = s_list[5]
    station_arr[ii][station_header[4]] = s_list[6]
    station_arr[ii][station_header[5]] = s_list[7]
    station_arr[ii][station_header[6]] = s_list[8]

# read velocity information
grid_line = lines[229].strip().split()
n_east, n_north, nz = [int(ii) for ii in [grid_line[5], grid_line[8], grid_line[11]]]

grid_east = np.array([float(jj) for jj in lines[232].strip().split()])
grid_north = np.array([float(jj) for jj in lines[235].strip().split()])
grid_z = np.array([float(jj) for jj in lines[238].strip().split()])

# read in first set of models, what ever those are
v_list = []

line_num = 244
for ii in range(nz * 3):
    v_lines = lines[line_num : line_num + n_north]
    l_list = []
    for line in v_lines:
        l_list.append([float(jj) for jj in line.strip().split()])

    v_arr = np.array(l_list)
    v_list.append(v_arr)
    line_num += n_north + 2

vp = np.array(v_list[0:nz]).T
vp_vs = np.array(v_list[nz : 2 * nz]).T
vs = np.array(v_list[2 * nz :]).T

# read final Vp model
f_vp = []

line_num = 12085
for ii in range(nz - 4):
    v_lines = lines[line_num : line_num + n_north]
    l_list = []
    for line in v_lines:
        l_list.append([float(jj) for jj in line.strip().split()])

    v_arr = np.array(l_list)
    f_vp.append(v_arr)
    line_num += n_north + 2

f_vp = np.array(f_vp).T

# read final Vs and Vp/Vs models
f_vpvs = []

line_num = 12699
for ii in range(2 * (nz - 4)):
    v_lines = lines[line_num : line_num + n_north]
    l_list = []
    for line in v_lines:
        l_list.append([float(jj) for jj in line.strip().split()])

    v_arr = np.array(l_list)
    f_vpvs.append(v_arr)
    line_num += n_north + 2

f_vpvs = np.array(f_vpvs).T

f_vs = f_vpvs[:, :, np.arange(1, f_vpvs.shape[2], 2)]
f_vp_vs = f_vpvs[:, :, np.arange(0, f_vpvs.shape[2], 2)]


# --> read in final earthquake locations
loc_header = lines[11819].strip().split()[3:]
loc_lines = lines[11820:12053]

eq_dtype = [(header, np.float) for header in loc_header]
eq_arr = np.zeros(len(loc_lines), dtype=eq_dtype)

for ii, line in enumerate(loc_lines):
    loc_list = line.replace("w", " ").replace("n", " ").strip().split()[4:]
    loc_list = [float(jj) for jj in loc_list]
    eq_arr[ii][loc_header[0]] = loc_list[0] + loc_list[1] / 60.0
    eq_arr[ii][loc_header[1]] = loc_list[2] + loc_list[3] / 60.0
    eq_arr[ii][loc_header[2]] = loc_list[4]
    eq_arr[ii][loc_header[3]] = loc_list[5]
    eq_arr[ii][loc_header[4]] = loc_list[6]
    eq_arr[ii][loc_header[5]] = loc_list[7]
    eq_arr[ii][loc_header[6]] = loc_list[8]
    eq_arr[ii][loc_header[7]] = loc_list[9]
    eq_arr[ii][loc_header[8]] = loc_list[10]

##-> write vtk files
# figure out shift in model centers
# mt_zone, mt_east, mt_north = ll2utm.LLtoUTM(23, modem_center[0], modem_center[1])
v_zone, v_east, v_north = ll2utm.LLtoUTM(23, v_lat, v_lon - 0.29)

shift_east = (mt_east - v_east + 4000) / 1000.0
shift_north = (mt_north - v_north + 1000) / 1000.0


# vtk_grid_east = np.append(grid_east, grid_east[-1]*1.1)-shift_east
# vtk_grid_north = np.append(grid_north, grid_north[-1]*1.1)-shift_north
vtk_grid_east = grid_east[1:-1] - shift_east
vtk_grid_north = grid_north[1:-1] - shift_north
vtk_grid_east = np.append(vtk_grid_east, vtk_grid_east[-1] * 1.1)
vtk_grid_north = np.append(vtk_grid_north, vtk_grid_north[-1] * 1.1)
vtk_gz = grid_z[2:-1] + 2

# vtk_vp = np.rot90(f_vp, 3)
vtk_vp = np.flipud(np.fliplr(np.rot90(f_vp[1:-1, 1:-1, :], 1)))
vtk_vs = np.flipud(np.fliplr(np.rot90(f_vs[1:-1, 1:-1, :], 1)))
vtk_d_vp = (vp[:, :, 2:-2] - f_vp[:, :, :]) * 100
vtk_d_vp = np.flipud(np.fliplr(np.rot90(vtk_d_vp[1:-1, 1:-1, :], 1)))
vtk_vp_vs = np.flipud(np.fliplr(np.rot90(f_vp_vs[1:-1, 1:-1, :], 1)))
a2vtk.gridToVTK(
    os.path.join(save_dir, "lv_3d_models", "foulger_2003_vp_rot_lvc"),
    vtk_grid_north,
    vtk_grid_east,
    vtk_gz,
    cellData={"Vp": vtk_vp.T, "d_Vp": vtk_d_vp.T, "Vp/Vs": vtk_vp_vs.T, "Vs": vtk_vs.T},
)
# a2vtk.gridToVTK(os.path.join(save_dir, 'foulger_2003_vp_lvc'),
#                vtk_grid_east,
#                vtk_grid_north,
#                vtk_gz,
#                cellData={'Vp': vtk_vp ,
#                          'd_Vp': vtk_d_vp})
# a2vtk.gridToVTK(os.path.join(save_dir, 'foulger_2003_vs_lvc'),
#                vtk_grid_east,
#                vtk_grid_north,
#                vtk_gz,
#                cellData={'Vs': f_vs,
#                          'd_Vs': vs[:, :, 2:-2]-f_vs})
# a2vtk.gridToVTK(os.path.join(save_dir, 'foulger_2003_vpvs_lvc'),
#                vtk_grid_east,
#                vtk_grid_north,
#                vtk_gz,
#                cellData={'Vp/Vs': f_vp_vs})
#
