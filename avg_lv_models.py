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
# mfn_no_tipper = r"/home/jpeacock/Documents/ModEM/LV/Inv1_dp_no_tipper/lv_no_tipper_NLCG_100.rho"
# mfn_tipper = r"/home/jpeacock/Documents/ModEM/LV/NAS/hs_tipper/lv_tipper_NLCG_029.rho"
# mfn_ws_hs1 = r"/home/jpeacock/Documents/wsinv3d/LV/Inv_lv_coarse_2/lv_fine_model.15"
# mfn_ws_sm1 = r"/home/jpeacock/Documents/wsinv3d/LV/sm_modem_inv2/lv_sm_modem_inv2_fine_model.07"
# mfn_ws_sm2 = r"/home/jpeacock/Documents/wsinv3d/LV/sm_modem_inv1/lv_sm_modem_inv1_fine_model.06"

# mfn_mb_sm = r"/home/jpeacock/Documents/ModEM/LV/mb_starting_inv1/lv_NLCG_067.rho"
mfn_sm3 = r"/home/jpeacock/Documents/ModEM/LV/hs1000_avg/lv_sm3_avg_err07_NLCG_067.rho"
# mfn_sm_mb_t = r"/home/jpeacock/Documents/ModEM/LV/sm_mb_tipper/lv_mb_tipper_NLCG_043.rho"
mfn_avg_1 = r"/home/jpeacock/Documents/ModEM/LV/sm_avg_inv1/lv_avg_err12_NLCG_051.rho"
mfn_sm_mb = r"/home/jpeacock/Documents/ModEM/LV/sm_mb_inv1/lv_mb_sm_err12_NLCG_071.rho"
mfn_avg_2 = (
    r"/home/jpeacock/Documents/ModEM/LV/sm_avg_inv2/lv_sm_avg_err07_NLCG_057.rho"
)
mfn_avg_3 = r"/home/jpeacock/Documents/ModEM/LV/sm_avg_all_cov5/lv_avg_all_NLCG_069.rho"
mfn_avg_sm1 = r"/home/jpeacock/Documents/ModEM/LV/sm_avg_cov5/lv_avg_cov5_NLCG_054.rho"

mfn_list = [mfn_sm3, mfn_sm_mb, mfn_avg_sm1, mfn_avg_1, mfn_avg_2, mfn_avg_3]

# difference between modem and ws grids
# d_east = -7500.
# d_north = 500.

# get all models into useable objects
modem_data = modem.Data()
modem_data.read_data_file(data_fn)

model_obj = modem.Model()
model_obj.read_model_file(mfn_list[3])


new_res = np.ones_like(model_obj.res_model)

for mfn in mfn_list:
    m_obj = modem.Model()
    m_obj.read_model_file(mfn)
    if m_obj.res_model.shape != model_obj.res_model.shape:
        new_res *= interp_grid(m_obj, model_obj)

    else:
        new_res[:, :, :] *= m_obj.res_model

# --> average all as a geometric mean
new_res = new_res ** (1.0 / len(mfn_list))

model_obj.res_model = new_res.copy()
model_obj.write_model_file(
    save_path=r"/home/jpeacock/Documents/ModEM/LV", model_fn_basename="lv_avg_all_5.rho"
)
mm = modem.ModelManipulator(model_obj.model_fn)
