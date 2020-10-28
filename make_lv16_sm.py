# -*- coding: utf-8 -*-
"""
Created on Mon Jan 12 13:43:30 2015

Average all existing model of long valley

@author: jpeacock
"""

import numpy as np
import mtpy.modeling.ws3dinv as ws
import mtpy.modeling.modem_new as modem
import matplotlib.pyplot as plt
import scipy.signal as sps
import scipy.interpolate as spi


def smooth_2d(res_array, window_len):
    """
    convolve a gaussian window for smoothing
    """

    gx, gy = np.mgrid[-window_len : window_len + 1, -window_len : window_len + 1]

    gauss = np.exp(-(gx ** 2 / float(window_len) + gy ** 2 / float(window_len)))
    gauss /= gauss.sum()

    smooth_array = sps.convolve(res_array, gauss, mode="same")

    return smooth_array


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
            old_model_obj.grid_north[:, None] + shift_north,
            old_model_obj.grid_east[None, :] + shift_east,
        )

        # 2) do a 2D interpolation for each layer, much faster
        new_res = np.zeros(
            (
                new_model_obj.grid_north.shape[0],
                new_model_obj.grid_east.shape[0],
                new_model_obj.grid_z.shape[0],
            )
        )

        for zz in range(new_model_obj.grid_z.shape[0]):
            try:
                old_zz = np.where(old_model_obj.grid_z >= new_model_obj.grid_z[zz])[0][
                    0
                ]
            except IndexError:
                old_zz = -1

            print "New depth={0:.2f}; old depth={1:.2f}".format(
                new_model_obj.grid_z[zz], old_model_obj.grid_z[old_zz]
            )

            new_res[:, :, zz] = spi.griddata(
                (north.ravel(), east.ravel()),
                old_model_obj.res_model[:, :, old_zz].ravel(),
                (new_model_obj.grid_north[:, None], new_model_obj.grid_east[None, :]),
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
            old_model_obj.grid_north[:, None, None],
            old_model_obj.grid_east[None, :, None],
            old_model_obj.grid_z[None, None, :],
        )

        # 2) next interpolate ont the new mesh (3D interpolation, slow)
        new_res = spi.griddata(
            (north.ravel(), east.ravel(), vert.ravel()),
            old_model_obj.res_model.ravel(),
            (
                new_model_obj.grid_north[:, None, None],
                new_model_obj.grid_east[None, :, None],
                new_model_obj.grid_z[None, None, :],
            ),
            method="linear",
        )

    print "Shape of new res = {0}".format(new_res.shape)
    return new_res


# ==============================================================================
#  interpolate all models onto the same grid
# ==============================================================================
data_fn = r"/home/jpeacock/Documents/ModEM/LV/lv_16_inv01/lv16_err05.dat"
mfn_lv_geo = r"/home/jpeacock/Documents/ModEM/LV/lv_geo_sm_avg_01/lv_geo_ws_err03_cov5_NLCG_054.rho"
mfn_lv16 = r"/home/jpeacock/Documents/ModEM/LV/lv_16_inv01/lv16_err05_cov3_NLCG_072.rho"
# difference between modem and ws grids
d_east = -1650.0
d_north = 6600.0

# get all models into useable objects
modem_data = modem.Data()
modem_data.read_data_file(data_fn)

base_model = modem.Model()
base_model.read_model_file(mfn_lv16)

modem_geo = modem.Model()
modem_geo.read_model_file(mfn_lv_geo)


# --> interpolate on to the base model

geo_sm = interp_grid(
    modem_geo, base_model, pad=2, shift_east=d_east, shift_north=d_north
)


# --> average all as a geometric mean
# avg_res = (nr_ws_hs1*nr_ws_sm1*nr_ws_sm2*nr_nt*nr_tip*\
#            nr_mb*nr_sm3)**(1./7)
# avg_res = (nr_ws_sm2*nr_tip*nr_sm3*nr_sm_mb_t*nr_sm_mb)**(1./5)
avg_res = (geo_sm * base_model.res_model) ** (1.0 / 2)
# avg_res = (nr_ws_hs1*nr_ws_sm1*nr_ws_sm2*nr_nt*nr_tip)**(1./5)

x, y = np.meshgrid(base_model.grid_east, base_model.grid_north)
kk = 30
kwargs = {"cmap": "jet_r", "vmin": -1, "vmax": 4}

fig = plt.figure(4)
ax1 = fig.add_subplot(1, 1, 1, aspect="equal")
ax1.pcolormesh(x, y, np.log10(avg_res[:, :, kk]), **kwargs)


# ax8 = fig.add_subplot(2,4,7, aspect='equal', sharex=ax1, sharey=ax1)
# ax8.pcolormesh(x, y, np.log10(nr_sm3[:, :, kk]), **kwargs)

for ax in [ax1]:
    ax.scatter(
        modem_data.data_array["rel_east"],
        modem_data.data_array["rel_north"],
        marker="v",
        c="k",
    )
plt.show()

base_model.res_model = avg_res.copy()
base_model.write_model_file(
    save_path=r"/home/jpeacock/Documents/ModEM/LV",
    model_fn_basename="lv16_geo_avg_sm.rho",
)
