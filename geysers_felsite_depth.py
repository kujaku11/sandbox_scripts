# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 14:54:24 2019

@author: jpeacock
"""

import pandas as pd
import numpy as np
from mtpy.modeling import modem
from scipy import interpolate

m_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\gz_z03_c02_074.rho"
fn_felsite = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\Top_Felsite_Points_WGS84_mc.csv"
m3_fn = (
    r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03\gz_err03_cov02_NLCG_057.rho"
)


def interp_grid(
    old_model_obj,
    new_model_obj,
    shift_east=0,
    shift_north=0,
    pad=1,
    dim="2d",
    smooth_kernel=None,
):
    """
    interpolate an old grid onto a new one
    """

    if dim == "2d":
        north, east = np.broadcast_arrays(
            old_model_obj.plot_north[:, None] + shift_north,
            old_model_obj.plot_east[None, :] + shift_east,
        )

        # 2) do a 2D interpolation for each layer, much faster
        new_res = np.zeros(
            (
                new_model_obj.plot_north.shape[0],
                new_model_obj.plot_east.shape[0],
                new_model_obj.plot_z.shape[0],
            )
        )

        for zz in range(new_model_obj.plot_z.shape[0]):
            try:
                old_zz = np.where(old_model_obj.plot_z >= new_model_obj.plot_z[zz])[0][
                    0
                ]
            except IndexError:
                old_zz = -1

            print(
                "New depth={0:.2f}; old depth={1:.2f}".format(
                    new_model_obj.plot_z[zz], old_model_obj.plot_z[old_zz]
                )
            )

            new_res[:, :, zz] = interpolate.griddata(
                (north.ravel(), east.ravel()),
                old_model_obj.res_model[:, :, old_zz].ravel(),
                (new_model_obj.plot_north[:, None], new_model_obj.plot_east[None, :]),
                method="linear",
            )

            new_res[0:pad, pad:-pad, zz] = new_res[pad, pad:-pad, zz]
            new_res[-pad:, pad:-pad, zz] = new_res[-pad - 1, pad:-pad, zz]
            new_res[:, 0:pad, zz] = (
                new_res[:, pad, zz].repeat(pad).reshape(new_res[:, 0:pad, zz].shape)
            )
            new_res[:, -pad:, zz] = (
                new_res[:, -pad - 1, zz]
                .repeat(pad)
                .reshape(new_res[:, -pad:, zz].shape)
            )

    elif dim == "3d":
        # 1) first need to make x, y, z have dimensions (nx, ny, nz), similar to res
        north, east, vert = np.broadcast_arrays(
            old_model_obj.plot_north[:, None, None],
            old_model_obj.plot_east[None, :, None],
            old_model_obj.plot_z[None, None, :],
        )

        # 2) next interpolate ont the new mesh (3D interpolation, slow)
        new_res = interpolate.griddata(
            (north.ravel(), east.ravel(), vert.ravel()),
            old_model_obj.res_model.ravel(),
            (
                new_model_obj.plot_north[:, None, None],
                new_model_obj.plot_east[None, :, None],
                new_model_obj.plot_z[None, None, :],
            ),
            method="linear",
        )

    print("Shape of new res = {0}".format(new_res.shape))
    return new_res


# =============================================================================
#
# =============================================================================
df_felsite = pd.read_csv(fn_felsite)
for col in df_felsite.columns:
    df_felsite[col] *= 1000


### open model
m_obj = modem.Model()
m_obj.read_model_file(m_fn)

### first need to interpolate depth data onto a similar map
grid_north, grid_east = np.meshgrid(m_obj.grid_north, m_obj.grid_east)

# --> felsite
f_points = np.array([df_felsite.northing, df_felsite.easting]).T
f_map = interpolate.griddata(
    f_points, df_felsite.depth, (grid_north, grid_east), method="cubic"
)

felsite = m_obj.res_model.copy()
for x_index, xx in enumerate(m_obj.grid_north):
    for y_index, yy in enumerate(m_obj.grid_east):
        f_depth = f_map[y_index, x_index]
        if np.isnan(f_depth):
            continue
        #            f_depth = np.nanmax(f_map)
        z_index = np.where(m_obj.grid_z <= f_depth)
        try:
            felsite[x_index, y_index, z_index] = 1e12
        except IndexError:
            pass


felsite[np.where(m_obj.res_model > 1e11)] = 1e12
felsite[np.where(m_obj.res_model < 45)] = 1e12

### gonna have to interpolate
m3_obj = modem.Model()
m3_obj.read_model_file(m3_fn)

m3_res = interp_grid(m3_obj, m_obj)
# felsite = np.sqrt(felsite * m3_res)
avg_res = np.sqrt(m3_res * m_obj.res_model)

# m3_obj.res_model = avg_res
# m3_obj.write_model_file(model_fn_basename=r"gz_avg.rho")
# m3_obj.write_vtk_file(vtk_fn_basename=r"gz_avg")
#### add in the extensions
# n_limits = (-500, 6000)
# e_limits = (-6000, 6000)
# z_limits = (1000, 60000)
#
# n1 = np.where((m_obj.grid_north > n_limits[0]) &
#              (m_obj.grid_north < n_limits[1]))[0]
# e1 = np.where((m_obj.grid_east > e_limits[0]) &
#              (m_obj.grid_east < e_limits[1]))[0]
# z1 = np.where((m_obj.grid_z > z_limits[0]) &
#              (m_obj.grid_z < z_limits[1]))[0]
#
# felsite[n1[0]:n1[-1], e1[0]:e1[-1], z1[0]:z1[-1]] = m3_res[n1[0]:n1[-1],
#        e1[0]:e1[-1], z1[0]:z1[-1]] + 15

# m_obj.res_model = felsite
# m_obj.write_vtk_file(vtk_fn_basename='geysers_felsite_mixed')
# m_obj.write_model_file(model_fn_basename='gz_felsite_mixed.rho')

m_obj.res_model = avg_res
m_obj.write_vtk_file(vtk_fn_basename="geysers_avg")
m_obj.write_model_file(model_fn_basename="gz_avg.rho")
