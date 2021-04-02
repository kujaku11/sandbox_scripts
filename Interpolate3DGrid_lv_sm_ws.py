# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 14:42:53 2014

@author: jpeacock-pr
"""


import mtpy.modeling.modem_new as modem
import scipy.interpolate as spi
import numpy as np
import time
import matplotlib.pyplot as plt
import mtpy.modeling.ws3dinv as ws

data_fn = r"/home/jpeacock/Documents/ModEM/LV/sm_comb_inv2/lv_dp_err7.dat"

old_model_fn = r"/home/jpeacock/Documents/ModEM/LV/sm_comb_inv2/lv_comb_smooth.rho"
ws_model_fn = r"/home/jpeacock/Documents/wsinv3d/LV/Inv_lv_coarse_2/lv_fine_model.15"


interpolation_dim = "2d"

shift_east = -7200
shift_north = 500

data_obj = modem.Data()
data_obj.read_data_file(data_fn)

old_mod = modem.Model()
old_mod.read_model_file(old_model_fn)

new_mod = modem.Model()
new_mod.station_locations = data_obj.station_locations.copy()
new_mod.cell_size_east = 500
new_mod.cell_size_north = 500
new_mod.n_layers = 40
new_mod.pad_east = 10
new_mod.pad_north = 10
new_mod.pad_z = 5
new_mod.pad_stretch_h = 1.7
new_mod.pad_stretch_v = 1.3
new_mod.z1_layer = 10
new_mod.z_target_depth = 40000
new_mod.z_bottom = 300000
new_mod.make_mesh()
new_mod.plot_mesh()

print "Start Time = {0}".format(time.ctime())

if interpolation_dim == "2d":
    pad = new_mod.pad_east / 2
    north, east = np.broadcast_arrays(
        old_mod.grid_north[:, None], old_mod.grid_east[None, :]
    )

    # 2) do a 2D interpolation for each layer, much faster
    new_res = np.zeros(
        (
            new_mod.grid_north.shape[0],
            new_mod.grid_east.shape[0],
            new_mod.grid_z.shape[0],
        )
    )

    for zz in range(new_mod.grid_z.shape[0]):
        try:
            old_zz = np.where(old_mod.grid_z >= new_mod.grid_z[zz])[0][0]
        except IndexError:
            old_zz = -1

        print "New depth={0:.2f}; old depth={1:.2f}".format(
            new_mod.grid_z[zz], old_mod.grid_z[old_zz]
        )

        new_res[:, :, zz] = spi.griddata(
            (north.ravel(), east.ravel()),
            old_mod.res_model[:, :, old_zz].ravel(),
            (new_mod.grid_north[:, None], new_mod.grid_east[None, :]),
            method="linear",
        )

        new_res[0:pad, pad:-pad, zz] = new_res[pad, pad:-pad, zz]
        new_res[-pad:, pad:-pad, zz] = new_res[-pad - 1, pad:-pad, zz]
        new_res[:, 0:pad, zz] = (
            new_res[:, pad, zz].repeat(pad).reshape(new_res[:, 0:pad, zz].shape)
        )
        new_res[:, -pad:, zz] = (
            new_res[:, -pad - 1, zz].repeat(pad).reshape(new_res[:, -pad:, zz].shape)
        )

elif interpolation_dim == "3d":
    # 1) first need to make x, y, z have dimensions (nx, ny, nz), similar to res
    north, east, vert = np.broadcast_arrays(
        old_mod.grid_north[:, None, None],
        old_mod.grid_east[None, :, None],
        old_mod.grid_z[None, None, :],
    )

    # 2) next interpolate ont the new mesh (3D interpolation, slow)
    new_res = spi.griddata(
        (north.ravel(), east.ravel(), vert.ravel()),
        old_mod.res_model.ravel(),
        (
            new_mod.grid_north[:, None, None],
            new_mod.grid_east[None, :, None],
            new_mod.grid_z[None, None, :],
        ),
        method="linear",
    )


#
new_res[np.where(np.nan_to_num(new_res) == 0.0)] = 100.0
new_mod.res_model = new_res

new_mod.write_model_file(
    save_path=r"/home/jpeacock/Documents/ModEM/LV/sm_comb_inv2",
    model_fn_basename="ModEM_lv_starting_model_comb.rho",
)

x, y = np.meshgrid(new_mod.grid_east, new_mod.grid_north)
fig = plt.figure(2)
ax1 = fig.add_subplot(1, 1, 1, aspect="equal")
ax1.pcolormesh(x, y, np.log10(new_res[:, :, 30]), cmap="jet_r", vmin=-1, vmax=4)
plt.show()


print "End Time = {0}".format(time.ctime())
