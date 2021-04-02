# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 14:00:42 2014

combine meshes

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np
import scipy.interpolate as spi
import scipy.signal as sps
import matplotlib.pyplot as plt

from mtpy.modeling import modem

# =============================================================================
# Functions for combining meshes
# =============================================================================
def smooth_2d(res_array, window_len):
    """
    convolve a gaussian window for smoothing
    """

    gx, gy = np.mgrid[-window_len : window_len + 1, -window_len : window_len + 1]

    gauss = np.exp(-(gx ** 2 / float(window_len) + gy ** 2 / float(window_len)))
    gauss /= gauss.sum()

    smooth_array = sps.convolve(res_array, gauss, mode="same")

    return smooth_array


def pad_res_model(res_array, pad):
    for zz in range(res_array.shape[2]):
        res_array[0:pad, pad:-pad, zz] = res_array[pad, pad:-pad, zz]
        res_array[-pad:, pad:-pad, zz] = res_array[-pad - 1, pad:-pad, zz]
        res_array[:, 0:pad, zz] = (
            res_array[:, pad, zz].repeat(pad).reshape(res_array[:, 0:pad, zz].shape)
        )
        res_array[:, -pad:, zz] = (
            res_array[:, -pad - 1, zz]
            .repeat(pad)
            .reshape(res_array[:, -pad:, zz].shape)
        )

    return res_array


def fill_outside_grid(res_array, n_pad, avg_range):
    x_range = np.append(np.arange(avg_range), np.arange(-avg_range, 0, 1))
    y_range = np.append(np.arange(avg_range), np.arange(-avg_range, 0, 1))

    x_index, y_index = np.meshgrid(x_range, y_range)
    for zz in range(res_array.shape[2]):
        avg_res_value = np.mean(
            [
                np.median(res_array[x_index, y_index, zz]),
                np.median(res_array[avg_range:-avg_range, 0:avg_range, zz]),
                np.median(res_array[avg_range:-avg_range, -avg_range:, zz]),
                np.median(res_array[0:avg_range, avg_range:-avg_range, zz]),
                np.median(res_array[-avg_range:, avg_range:-avg_range, zz]),
            ]
        )

        res_array[x_index, y_index, zz] = avg_res_value
        res_array[n_pad:-n_pad, 0:n_pad, zz] = avg_res_value
        res_array[n_pad:-n_pad, -n_pad:, zz] = avg_res_value
        res_array[0:n_pad, n_pad:-n_pad, zz] = avg_res_value
        res_array[-n_pad:, n_pad:-n_pad, zz] = avg_res_value
        print "avg res for {0:>8.2f} m = {1:>8.2f}".format(zz, avg_res_value)

    return res_array


# ==============================================================================
# interpolate
# ==============================================================================
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

            print "New depth={0:.2f}; old depth={1:.2f}".format(
                new_model_obj.plot_z[zz], old_model_obj.plot_z[old_zz]
            )

            new_res[:, :, zz] = spi.griddata(
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

            if smooth_kernel is not None:
                new_res[:, :, zz] = smooth_2d(new_res[:, :, zz], smooth_kernel)

    elif dim == "3d":
        # 1) first need to make x, y, z have dimensions (nx, ny, nz), similar to res
        north, east, vert = np.broadcast_arrays(
            old_model_obj.plot_north[:, None, None],
            old_model_obj.plot_east[None, :, None],
            old_model_obj.plot_z[None, None, :],
        )

        # 2) next interpolate ont the new mesh (3D interpolation, slow)
        new_res = spi.griddata(
            (north.ravel(), east.ravel(), vert.ravel()),
            old_model_obj.res_model.ravel(),
            (
                new_model_obj.plot_north[:, None, None],
                new_model_obj.plot_east[None, :, None],
                new_model_obj.plot_z[None, None, :],
            ),
            method="linear",
        )

    print "Shape of new res = {0}".format(new_res.shape)
    return new_res


# ==============================================================================
#
# ==============================================================================
# --> file names of models to combine
# lv_model_fn = r"/home/jpeacock/Documents/wsinv3d/LV/Inv_dp/lv_dp_fine_model.04_03"
lv_model_fn = r"c:\Users\jpeacock\Documents\LV\Inversions\lv_mb_sm_edited.rho"

# mb_model_fn = r"/home/jpeacock/Documents/ModEM/MB_MT/WS_StartingModel_03_tipper/cov3_mb_tipper_NLCG_028.rho"
# mb_model_fn = r"c:\Users\jpeacock\Documents\MonoBasin\cov3_mb_tipper_NLCG_028.rho"

# grid already made, use it to combine the models
comb_model_fn = (
    r"c:\Users\jpeacock\Documents\MonoBasin\modem_inv\inv_02\ml_sm02_lake.rho"
)

# locate model centers (E, N)
# mb_center = (327150., 4194900.)
# lv_center old lv_center = (336800, 4167525)
lv_center = (331534.0, 4179614.0)
# comb_center = (331515+5285, 4179690) # big center
comb_center = (328520.0, 4201968.0)

# --> read in the model files
lv_mod = modem.Model()
lv_mod.read_model_file(lv_model_fn)

# mb_mod = modem.Model()
# mb_mod.read_model_file(mb_model_fn)

comb_mod = modem.Model()
comb_mod.read_model_file(comb_model_fn)

# --> interpolate each grid onto the combined grid
# mb_res = interp_grid(mb_mod,
#                     comb_mod,
#                     shift_east=-comb_center[0]+mb_center[0],
#                     shift_north=-comb_center[1]+mb_center[1],
#                     pad=1,
#                     dim='2d',
#                     smooth_kernel=None)
lv_res = interp_grid(
    lv_mod,
    comb_mod,
    shift_east=-comb_center[0] + lv_center[0],
    shift_north=-comb_center[1] + lv_center[1],
    pad=1,
    dim="2d",
    smooth_kernel=None,
)

#
# mb_nan = np.where(np.nan_to_num(mb_res) == 0)
# mb_res[mb_nan] = mb_res[np.where(np.nan_to_num(mb_res) != 0)].mean()
# mb_res[mb_res > 5000.00] = 5000
#
# combine the resistivity models into one
comb_res = lv_res.copy()

# make sure there are no nan
# comb_res[np.where(np.nan_to_num(comb_res) == 0)] = 100.00
#
# smooth_comb_res = fill_outside_grid(comb_res, 3, 3)

smooth_comb_res = comb_res.copy()
for zz in range(comb_mod.plot_z.shape[0]):
    smooth_comb_res[:, :, zz] = 10 ** smooth_2d(np.log10(smooth_comb_res[:, :, zz]), 5)

smooth_comb_res = fill_outside_grid(smooth_comb_res, 3, 12)

comb_mod.res_model = smooth_comb_res
comb_mod.write_model_file(
    save_path=r"c:\Users\jpeacock\Documents\MonoBasin\modem_inv\inv_03",
    model_fn_basename=r"lv_mb_sm.rho",
)


# --> plot to see how we did
plot_east, plot_north = np.meshgrid(comb_mod.plot_east, comb_mod.plot_north)

md = modem.Data()
md.read_data_file(
    r"c:\Users\jpeacock\Documents\MonoBasin\modem_inv\inv_02\ml_modem_data_z05_t02.dat"
)

fig = plt.figure(3)
plt.clf()

# ax_mb = fig.add_subplot(1, 3, 1, aspect='equal')
# ax_mb.pcolormesh(plot_east, plot_north, np.log10(mb_res[:, :, 33]),
#                 cmap='jet_r',
#                 vmin=-1,
#                 vmax=4)

ax_lv = fig.add_subplot(1, 3, 1, aspect="equal")  # , sharex=ax_mb, sharey=ax_mb)
ax_lv.pcolormesh(
    plot_east, plot_north, np.log10(lv_res[:, :, 33]), cmap="jet_r", vmin=-1, vmax=4
)
ax_co = fig.add_subplot(1, 3, 2, aspect="equal", sharex=ax_lv, sharey=ax_lv)
ax_co.pcolormesh(
    plot_east, plot_north, np.log10(comb_res[:, :, 33]), cmap="jet_r", vmin=-1, vmax=4
)

ax_sm = fig.add_subplot(1, 3, 3, aspect="equal", sharex=ax_lv, sharey=ax_lv)
ax_sm.pcolormesh(
    plot_east,
    plot_north,
    np.log10(smooth_comb_res[:, :, 33]),
    cmap="jet_r",
    vmin=-1,
    vmax=4,
)

for ax in [ax_lv, ax_co, ax_sm]:
    ax.scatter(
        md.data_array["rel_east"], md.data_array["rel_north"], marker="v", c="k", s=10
    )
plt.show()


##--> plot the grids to see what the overlap is
# fig = plt.figure(1,)
# ax1 = fig.add_subplot(1, 1, 1, aspect='equal')
#
# line_list = []
# label_list = []
#
##for mod_obj, center, lc, label in zip([lv_mod, mb_mod, comb_mod],
##                               [lv_center, mb_center, comb_center],
##                               ['blue', 'brown', 'red'],
##                               ['lv', 'mb', 'comb'] ):
# for mod_obj, center, lc, label in zip([lv_mod, mb_mod],
#                               [lv_center, mb_center],
#                               ['blue', 'brown'],
#                               ['lv', 'mb']):
#    #plot the grid if desired
#    dx = center[0]
#    dy = center[1]
#
#    east_line_xlist = []
#    east_line_ylist = []
#    for xx in mod_obj.grid_east:
#        east_line_xlist.extend([xx+dx, xx+dx])
#        east_line_xlist.append(None)
#        east_line_ylist.extend([mod_obj.grid_north.min()+dy,
#                                mod_obj.grid_north.max()+dy])
#        east_line_ylist.append(None)
#    l1, =ax1.plot(east_line_xlist,
#                  east_line_ylist,
#                  lw=.5,
#                  color=lc)
#
#    north_line_xlist = []
#    north_line_ylist = []
#    for yy in mod_obj.grid_north:
#        north_line_xlist.extend([mod_obj.grid_east.min()+dx,
#                                 mod_obj.grid_east.max()+dx])
#        north_line_xlist.append(None)
#        north_line_ylist.extend([yy+dy, yy+dy])
#        north_line_ylist.append(None)
#    l1, =ax1.plot(north_line_xlist,
#                  north_line_ylist,
#                  lw=.5,
#                  color=lc)
#    line_list.append(l1)
#    label_list.append(label)
#
# ax1.set_xlabel('Easting (m)')
# ax1.set_ylabel('Northing (m)')
# ax1.legend(line_list, label_list)
#
#
# plt.show()
