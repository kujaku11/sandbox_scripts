# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 18:47:08 2017

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import mtpy.modeling.modem as modem
import os
import numpy as np
import datetime

# =============================================================================
# Inputs
# =============================================================================
# dfn = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\modem_inv\mnp_02\mnp_modem_data_z05_t02_edited.dat"
# dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_topo_inv_02\gv_modem_data_z03_t02_topo_edited.dat"
dfn = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\EasternMojave\modem_inv\inv_01\mj_modem_data_z05_t02_edited.dat"
remove_stations = []
shady_stations_zx = []
shady_stations_zy = []
shady_stations_t = []
remove_x = []
remove_y = []
flip_phase_x = []
flip_phase_y = []
static_shift_x = []
static_shift_y = []
swap_channel = []

add_err_z = 10
add_err_t = 0.15
add_err_period_range = None
elevation_bool = True

inv_modes = ["1"]
z_err_value = 5.0
t_err_value = 0.02
z_err_type = "eigen_floor"
t_err_type = "abs_floor"

# sv_fn = os.path.basename(dfn)[0:os.path.basename(dfn).find('_')]
sv_fn = "mj"
log_fn = os.path.join(os.path.dirname(dfn), "{0}_change_data_file.log".format(sv_fn))
# =============================================================================
# change data file
# =============================================================================
d_obj = modem.Data()
d_obj.read_data_file(dfn)

### add error to certain stations
if shady_stations_zx is not None:
    for e_station in shady_stations_zx:
        s_find = np.where(d_obj.data_array["station"] == e_station)[0][0]
        d_obj.data_array[s_find]["z_err"][:, 0, :] *= add_err_z

### add error to certain stations
if shady_stations_zy is not None:
    for e_station in shady_stations_zy:
        s_find = np.where(d_obj.data_array["station"] == e_station)[0][0]
        d_obj.data_array[s_find]["z_err"][:, 1, :] *= add_err_z

if shady_stations_t is not None:
    for e_station in shady_stations_t:
        s_find = np.where(d_obj.data_array["station"] == e_station)[0][0]
        d_obj.data_array[s_find]["tip_err"] += add_err_t

### remove a bad station
if remove_stations is not None:
    for b_station in remove_stations:
        s_find = np.where(d_obj.data_array["station"] == b_station)[0][0]
        d_obj.data_array[s_find]["z"][:] = 0
        d_obj.data_array[s_find]["z_err"][:] = 0
        d_obj.data_array[s_find]["tip"][:] = 0
        d_obj.data_array[s_find]["tip_err"][:] = 0

### remove x component
if remove_x is not None:
    for b_station in remove_x:
        s_find = np.where(d_obj.data_array["station"] == b_station)[0][0]
        d_obj.data_array[s_find]["z"][:, 0, :] = 0
        d_obj.data_array[s_find]["z_err"][:, 0, :] = 0

### remove y component
if remove_y is not None:
    for b_station in remove_y:
        s_find = np.where(d_obj.data_array["station"] == b_station)[0][0]
        d_obj.data_array[s_find]["z"][:, 1, :] = 0
        d_obj.data_array[s_find]["z_err"][:, 1, :] = 0

### flip x phase
if flip_phase_x is not None:
    for b_station in flip_phase_x:
        s_find = np.where(d_obj.data_array["station"] == b_station)[0][0]
        d_obj.data_array[s_find]["z"][:, 0, :] *= -1

### flip x phase
if flip_phase_y is not None:
    for b_station in flip_phase_y:
        s_find = np.where(d_obj.data_array["station"] == b_station)[0][0]
        d_obj.data_array[s_find]["z"][:, 1, :] *= -1

### static shift x
if static_shift_x is not None:
    for b_station, ss in static_shift_x:
        s_find = np.where(d_obj.data_array["station"] == b_station)[0][0]
        d_obj.data_array[s_find]["z"][:, 0, :] *= ss

### static shift y
if static_shift_y is not None:
    for b_station, ss in static_shift_y:
        s_find = np.where(d_obj.data_array["station"] == b_station)[0][0]
        d_obj.data_array[s_find]["z"][:, 1, :] *= ss

### swap channel z [(station, ((ii_1, jj_1), (ii_2, jj_2)))]
if swap_channel is not None:
    for b_station, ss in swap_channel:
        s_find = np.where(d_obj.data_array["station"] == b_station)[0][0]
        z1 = d_obj.data_array[s_find]["z"][:, ss[0][0], ss[0][1]].copy()
        z2 = d_obj.data_array[s_find]["z"][:, ss[1][0], ss[1][1]].copy()
        d_obj.data_array[s_find]["z"][:, ss[0][0], ss[0][1]] = z2
        d_obj.data_array[s_find]["z"][:, ss[1][0], ss[1][1]] = z1

### add period error
if add_err_period_range is not None:
    err_periods = np.where(
        (d_obj.period_list >= add_err_period_range[0])
        & (d_obj.period_list <= add_err_period_range[1])
    )
    d_obj.data_array["z_err"][:, err_periods, :, :] *= add_err_z

for inv_mode in inv_modes:
    d_obj.error_type_z = z_err_type
    d_obj.error_type_tipper = t_err_type
    d_obj.inv_mode = inv_mode
    d_obj.error_value_z = z_err_value
    d_obj.error_value_tipper = t_err_value

    if d_obj.inv_mode == "2":
        d_obj.write_data_file(
            save_path=os.path.dirname(dfn),
            fn_basename="{0}_modem_data_z{1:02.0f}.dat".format(
                sv_fn, d_obj.error_value_z
            ),
            fill=False,
            compute_error=True,
            elevation=elevation_bool,
        )
    elif d_obj.inv_mode == "5":
        d_obj.write_data_file(
            save_path=os.path.dirname(dfn),
            fn_basename="{0}_modem_data_t{1:02.0f}.dat".format(
                sv_fn, d_obj.error_value_tipper * 100
            ),
            fill=False,
            compute_error=True,
            elevation=elevation_bool,
        )
    else:
        d_obj.write_data_file(
            save_path=os.path.dirname(dfn),
            fn_basename="{0}_modem_data_z{1:02.0f}_t{2:02.0f}.dat".format(
                sv_fn, d_obj.error_value_z, d_obj.error_value_tipper * 100
            ),
            fill=False,
            compute_error=True,
            elevation=elevation_bool,
        )


# =============================================================================
# write a log file
# =============================================================================

lines = []
lines.append("\n" + "=" * 70)
lines.append("Change Date = {0}".format(datetime.datetime.now().isoformat()))
lines.append("dfn = {0}".format(dfn))
lines.append("remove_stations = {0}".format(remove_stations))
lines.append("shady_stations_zx = {0}".format(shady_stations_zx))
lines.append("shady_stations_zy = {0}".format(shady_stations_zy))
lines.append("shady_stations_t = {0}".format(shady_stations_t))
lines.append("remove_x = {0}".format(remove_x))
lines.append("remove_y = {0}".format(remove_y))
lines.append("flip_phase_x = {0}".format(flip_phase_x))
lines.append("flip_phase_y = {0}".format(flip_phase_y))
lines.append("static_shift_x = {0}".format(static_shift_x))
lines.append("static_shift_y = {0}".format(static_shift_y))
lines.append("swap_channel = {0}".format(swap_channel))
lines.append("add_err_z = {0}".format(add_err_z))
lines.append("add_err_t = {0}".format(add_err_t))
lines.append("elevation_bool = {0}".format(elevation_bool))
lines.append("inv_modes = {0}".format(inv_modes))
lines.append("z_err_value = {0}".format(z_err_value))
lines.append("t_err_value = {0}".format(t_err_value))
lines.append("z_err_type = {0}".format(z_err_type))
lines.append("t_err_type = {0}".format(t_err_type))

if os.path.exists(log_fn):
    with open(log_fn, "a") as log_fid:
        log_fid.write("\n".join(lines))
else:
    with open(log_fn, "w+") as log_fid:
        log_fid.write("\n".join(lines))
