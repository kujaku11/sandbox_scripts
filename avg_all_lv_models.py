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
data_fn = r"/home/jpeacock/Documents/ModEM/LV/sm_comb_inv2/lv_dp_err7.dat"
mfn_no_tipper = (
    r"/home/jpeacock/Documents/ModEM/LV/Inv1_dp_no_tipper/lv_no_tipper_NLCG_100.rho"
)
mfn_tipper = r"/home/jpeacock/Documents/ModEM/LV/NAS/hs_tipper/lv_tipper_NLCG_029.rho"
mfn_ws_hs1 = r"/home/jpeacock/Documents/wsinv3d/LV/Inv_lv_coarse_2/lv_fine_model.15"
mfn_ws_sm1 = (
    r"/home/jpeacock/Documents/wsinv3d/LV/sm_modem_inv2/lv_sm_modem_inv2_fine_model.07"
)
mfn_ws_sm2 = (
    r"/home/jpeacock/Documents/wsinv3d/LV/sm_modem_inv1/lv_sm_modem_inv1_fine_model.06"
)
mfn_avg_sm1 = r"/home/jpeacock/Documents/ModEM/LV/sm_avg_cov5/lv_avg_cov5_NLCG_054.rho"
mfn_mb_sm = r"/home/jpeacock/Documents/ModEM/LV/mb_starting_inv1/lv_NLCG_067.rho"
mfn_sm3 = r"/home/jpeacock/Documents/ModEM/LV/hs1000_avg/lv_sm3_avg_err07_NLCG_067.rho"
mfn_sm_mb_t = (
    r"/home/jpeacock/Documents/ModEM/LV/sm_mb_tipper/lv_mb_tipper_NLCG_043.rho"
)
mfn_sm_mb = r"/home/jpeacock/Documents/ModEM/LV/sm_mb_inv1/lv_mb_sm_err12_NLCG_071.rho"

# difference between modem and ws grids
d_east = -7500.0
d_north = 500.0

# get all models into useable objects
modem_data = modem.Data()
modem_data.read_data_file(data_fn)

base_model = modem.Model()
base_model.read_model_file(mfn_avg_sm1)

ws_hs1 = ws.WSModel(mfn_ws_hs1)
ws_sm1 = ws.WSModel(mfn_ws_sm1)
ws_sm2 = ws.WSModel(mfn_ws_sm2)

modem_nt = modem.Model()
modem_nt.read_model_file(mfn_no_tipper)

modem_tip = modem.Model()
modem_tip.read_model_file(mfn_tipper)

modem_sm_mb = modem.Model()
modem_sm_mb.read_model_file(mfn_mb_sm)

modem_sm3 = modem.Model()
modem_sm3.read_model_file(mfn_sm3)

modem_sm_mb_t = modem.Model()
modem_sm_mb_t.read_model_file(mfn_sm_mb_t)

modem_sm_mb_2 = modem.Model()
modem_sm_mb_2.read_model_file(mfn_sm_mb)

# --> interpolate on to the base model
# smooth over the ws models because their resistivities are so low and
# the models are coarse.
nr_ws_hs1 = interp_grid(
    ws_hs1, base_model, shift_east=d_east, shift_north=d_north, smooth_kernel=7, pad=5
)
nr_ws_sm1 = interp_grid(
    ws_sm1, base_model, shift_east=d_east, shift_north=d_north, smooth_kernel=7, pad=5
)
nr_ws_sm2 = interp_grid(
    ws_sm2, base_model, shift_east=d_east, shift_north=d_north, smooth_kernel=7, pad=5
)

nr_nt = interp_grid(modem_nt, base_model, pad=2)
nr_tip = interp_grid(modem_tip, base_model, pad=2)
nr_mb = interp_grid(modem_sm_mb, base_model, pad=2)
nr_sm3 = interp_grid(modem_sm3, base_model, pad=2)
nr_sm_mb_t = interp_grid(modem_sm_mb_t, base_model, pad=2)
nr_sm_mb = interp_grid(modem_sm_mb_2, base_model, pad=2)


# --> average all as a geometric mean
# avg_res = (nr_ws_hs1*nr_ws_sm1*nr_ws_sm2*nr_nt*nr_tip*\
#            nr_mb*nr_sm3)**(1./7)
# avg_res = (nr_ws_sm2*nr_tip*nr_sm3*nr_sm_mb_t*nr_sm_mb)**(1./5)
avg_res = (nr_ws_sm2 * nr_sm3 * nr_sm_mb_t) ** (1.0 / 3)
# avg_res = (nr_ws_hs1*nr_ws_sm1*nr_ws_sm2*nr_nt*nr_tip)**(1./5)

x, y = np.meshgrid(base_model.grid_east, base_model.grid_north)
kk = 30
kwargs = {"cmap": "jet_r", "vmin": -1, "vmax": 4}

fig = plt.figure(4)
ax1 = fig.add_subplot(2, 4, 1, aspect="equal")
ax1.pcolormesh(x, y, np.log10(nr_ws_sm2[:, :, kk]), **kwargs)

ax2 = fig.add_subplot(2, 4, 2, aspect="equal", sharex=ax1, sharey=ax1)
ax2.pcolormesh(x, y, np.log10(nr_tip[:, :, kk]), **kwargs)

ax3 = fig.add_subplot(2, 4, 3, aspect="equal", sharex=ax1, sharey=ax1)
ax3.pcolormesh(x, y, np.log10(nr_mb[:, :, kk]), **kwargs)

ax4 = fig.add_subplot(2, 4, 4, aspect="equal", sharex=ax1, sharey=ax1)
ax4.pcolormesh(x, y, np.log10(nr_sm3[:, :, kk]), **kwargs)

ax5 = fig.add_subplot(2, 4, 5, aspect="equal", sharex=ax1, sharey=ax1)
ax5.pcolormesh(x, y, np.log10(nr_sm_mb_t[:, :, kk]), **kwargs)

ax6 = fig.add_subplot(2, 4, 6, aspect="equal", sharex=ax1, sharey=ax1)
ax6.pcolormesh(x, y, np.log10(nr_sm_mb[:, :, kk]), **kwargs)

ax7 = fig.add_subplot(2, 4, 8, aspect="equal", sharex=ax1, sharey=ax1)
ax7.pcolormesh(x, y, np.log10(avg_res[:, :, kk]), **kwargs)

# ax8 = fig.add_subplot(2,4,7, aspect='equal', sharex=ax1, sharey=ax1)
# ax8.pcolormesh(x, y, np.log10(nr_sm3[:, :, kk]), **kwargs)

for ax in [ax1, ax2, ax3, ax4, ax5, ax6, ax7]:
    ax.scatter(
        modem_data.data_array["rel_east"],
        modem_data.data_array["rel_north"],
        marker="v",
        c="k",
    )
plt.show()

base_model.res_model = avg_res.copy()
base_model.write_model_file(
    save_path=r"/home/jpeacock/Documents/ModEM/LV", model_fn_basename="lv_avg_all_3.rho"
)
