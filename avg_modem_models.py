# -*- coding: utf-8 -*-
"""
Created on Mon Jan 12 13:43:30 2015

Average all existing model of long valley

@author: jpeacock
"""

import numpy as np
import mtpy.modeling.modem as modem
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
dfn = r"/home/jpeacock/Documents/ModEM/LV/hs1000_no_tipper/lv_dp_23p_no_tipper.dat"
mfn_no_tipper = (
    r"/home/jpeacock/Documents/ModEM/LV/hs1000_no_tipper/hs1000_no_tipper_NLCG_070.rho"
)
mfn_tipper = (
    r"/home/jpeacock/Documents/ModEM/LV/hs1000_tipper/hs1000_tipper_NLCG_042.rho"
)

modem_data = modem.Data()
modem_data.read_data_file(dfn)

modem_nt = modem.Model()
modem_nt.read_model_file(mfn_no_tipper)

modem_tip = modem.Model()
modem_tip.read_model_file(mfn_tipper)

# --> average all as a geometric mean
avg_res = (modem_nt.res_model * modem_tip.res_model) ** (1.0 / 2)
# avg_res = (nr_ws_hs1*nr_ws_sm1*nr_ws_sm2*nr_nt*nr_tip)**(1./5)

x, y = np.meshgrid(modem_tip.grid_east, modem_tip.grid_north)
kk = 30
kwargs = {"cmap": "jet_r", "vmin": -1, "vmax": 4}

fig = plt.figure(4)
ax1 = fig.add_subplot(1, 3, 1, aspect="equal")
ax1.pcolormesh(x, y, np.log10(modem_nt.res_model[:, :, kk]), **kwargs)

ax2 = fig.add_subplot(1, 3, 2, aspect="equal", sharex=ax1, sharey=ax1)
ax2.pcolormesh(x, y, np.log10(modem_tip.res_model[:, :, kk]), **kwargs)

ax3 = fig.add_subplot(1, 3, 3, aspect="equal", sharex=ax1, sharey=ax1)
ax3.pcolormesh(x, y, np.log10(avg_res[:, :, kk]), **kwargs)


for ax in [ax1, ax2, ax3]:
    ax.scatter(
        modem_data.data_array["rel_east"],
        modem_data.data_array["rel_north"],
        marker="v",
        c="k",
    )
plt.show()

modem_nt.res_model = avg_res.copy()
modem_nt.write_model_file(model_fn_basename="lv_avg_sm3.rho")
