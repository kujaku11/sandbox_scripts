# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 14:54:24 2019

@author: jpeacock

Estimate the resitivity within the steam field by using surfaces from the top
of steam and the top of the felsite.

"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd
import numpy as np
from mtpy.modeling import StructuredGrid3D
from scipy import interpolate

from matplotlib import pyplot as plt

# =============================================================================
### 2021
# m_fn = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2021\gz_2021_z03_c02_048.rho"
# )
### 2022
# m_fn = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2022\gz_2022_z03_c02_132.rho"
# )
### 2023
# m_fn = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2023\gz_2023_z03_c02_065.rho"
# )
### joint 2021
# m_fn = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\gz_joint_2021_z03_c02_NLCG_057.rho"
# )
### joint 2023
m_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\gz_joint_2023_z03_c02_NLCG_108.rho"
)

fn_steam = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\tos_points_cec_larger_grid_02.csv"
)
fn_felsite = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\Top_Felsite_Points_WGS84_cec_larger_grid_02.csv"
)

# read in the top of steam and top of felsite files
df_steam = pd.read_csv(fn_steam)
df_felsite = pd.read_csv(fn_felsite)

# get units into meters
for col in df_steam.columns:
    df_steam[col] *= 1000
    df_felsite[col] *= 1000

# read in model file
m_obj = StructuredGrid3D()
m_obj.from_modem(m_fn)
m_obj.model_epsg = 32610
m_obj.center_point.latitude = 38.812566
m_obj.center_point.longitude = -122.796391

### first need to interpolate depth data onto a similar map
grid_north, grid_east = np.meshgrid(m_obj.grid_north, m_obj.grid_east)

# --> felsite
f_points = np.array([df_felsite.northing, df_felsite.easting]).T
f_map = interpolate.griddata(
    f_points, df_felsite.depth, (grid_north, grid_east), method="cubic"
)
# --> steam
s_points = np.array([df_steam.northing, df_steam.easting]).T
s_map = interpolate.griddata(
    s_points, df_steam.depth, (grid_north, grid_east), method="cubic"
)
s_map[np.where(s_map < 0)] = 0
s_map[np.where(s_map > 2300)] = 2300
# s_map[12:26, 26:41] =


steam = m_obj.res_model.copy()
steam[:, :, :] = 1e12
for x_index, xx in enumerate(m_obj.grid_north):
    for y_index, yy in enumerate(m_obj.grid_east):
        s_depth = s_map[y_index, x_index]
        if np.isnan(s_depth):
            continue
        else:
            f_depth = f_map[y_index, x_index]
            if np.isnan(f_depth):
                f_depth = 3000
            z_index = np.where(
                (m_obj.grid_z <= f_depth) & (m_obj.grid_z >= s_depth)
            )
            steam[x_index, y_index, z_index] = m_obj.res_model[
                x_index, y_index, z_index
            ]


steam[np.where(m_obj.res_model > 1e10)] = 1e12

m_obj.res_model = steam
# m_obj.to_vtk(vtk_fn_basename=f"{m_fn.stem}_steam_res_02")
# m_obj.to_modem(model_fn=m_fn.parent.joinpath(f"{m_fn.stem}_steam_res_02.rho"))

# estimate saturation
saturation = steam.copy()
saturation[np.where(saturation > 100000)] = np.nan

c_map = np.nanmean(saturation, axis=2)

plot_map = np.log10(c_map) / np.nanmax(np.log10(c_map))

m_obj.res_model = np.nan_to_num(
    plot_map.reshape((plot_map.shape[0], plot_map.shape[1], 1)), nan=0
)
m_obj.nodes_z = [0]

m_obj.to_raster(
    200,
    save_path=m_fn.parent,
    pad_north=7,
    pad_east=7,
    shift_east=-600,
    shift_north=2500,
    log10=False,
)

plt.figure(1)
ax = plt.subplot(1, 3, 1, aspect="equal")
plt.pcolormesh(grid_east, grid_north, s_map)
plt.colorbar()
plt.subplot(1, 3, 2, sharex=ax, sharey=ax, aspect="equal")
plt.pcolormesh(grid_east, grid_north, f_map)
plt.colorbar()
plt.subplot(1, 3, 3, sharex=ax, sharey=ax, aspect="equal")
plt.pcolormesh(grid_east, grid_north, plot_map.T)
plt.colorbar()
ax.set_xlim((-7000, 7000))
ax.set_ylim((-7000, 7000))
plt.show()
