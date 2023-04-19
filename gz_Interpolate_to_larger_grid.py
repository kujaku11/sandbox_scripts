# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 14:42:53 2014

@author: jpeacock-pr
"""
# =============================================================================
# Imports
# =============================================================================
from mtpy.modeling import modem
import scipy.interpolate as spi
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# Inputs
# =============================================================================
data_fn = r"/home/jpeacock/Documents/ModEM/LV/sm_comb_inv2/lv_dp_err7.dat"

model_2017 = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\modem_inv\inv03\gz_err03_cov02_NLCG_057.rho"
model_2021 = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\inv_2021_01\gz_z03_c03_109.rho"
data_2021 = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\inv_2021_01\gz_modem_data_z03_tec.dat"

center_2017 = {
    "lat": 38.831979,
    "lon": -122.828190,
    "elev": -1190,
    "east": 514912.45579220104,
    "north": 4298145.401102481,
}
center_2021 = {
    "lat": 38.812566,
    "lon": -122.796391,
    "elev": -1250.00,
    "east": 517677.2897953276,
    "north": 4295996.8523288965,
}

# difference between modem and ws grids
shift_east = -2765
shift_north = -2150
shift_vertical = 60
pad = 3


# read in modem model file
m_2017 = modem.Model()
m_2017.read_model_file(model_2017)

m_2021 = modem.Model()
m_2021.read_model_file(model_2021)

# make north and east arrays for WS, similar to meshgrid
m17_north, m17_east = np.broadcast_arrays(
    m_2017.grid_north[:-1, None], m_2017.grid_east[None, :-1]
)

# make a new resistivity array that will be filled by interpolation
new_res = np.zeros_like(m_2021.res_model)

# 2) do a 2D interpolation for each layer, much faster
for zz in range(m_2021.grid_z.shape[0] - 1):
    try:
        old_zz = np.where(m_2017.grid_z >= m_2021.grid_z[zz] + shift_vertical)[
            0
        ][0]
    except IndexError:
        old_zz = -1

    print(
        "New depth={0:.2f}; old depth={1:.2f}".format(
            m_2021.grid_z[zz], m_2021.grid_z[old_zz]
        )
    )

    # interpolate ws onto modem grid in 2D for each layer
    # be sure to shift the cell
    r = m_2017.res_model[:, :, old_zz].ravel()
    r[np.where(r > 10000)] = 50
    new_res[:, :, zz] = spi.griddata(
        (m17_north.ravel() - shift_north, m17_east.ravel() + shift_east),
        r,
        (m_2021.grid_north[:-1, None], m_2021.grid_east[None, :-1]),
        method="linear",
    )

    # at the edges push values from the center, this way there are no
    # sharp edges near the boundaries of the grid, it goes to a 1D earth
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


# make sure there are no NAN in the array
new_res[np.where(np.nan_to_num(new_res) == 0.0)] = 60.0
new_res[np.where(m_2021.res_model > 10000)] = 1e12

m_2021.res_model = new_res
m_2021.write_model_file(
    save_path=r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\inv_2021_01",
    model_fn_basename="gz_sm_2017.rho",
)

# --> see what it looks like
modem_data = modem.Data()
modem_data.read_data_file(data_2021)

x, y = np.meshgrid(m_2021.grid_east[:-1], m_2021.grid_north[:-1])
fig = plt.figure(3)
for ii, zz in enumerate(range(0, 40, 5), 1):
    ax = fig.add_subplot(3, 3, ii, aspect="equal")
    cp = ax.pcolormesh(
        x, y, np.log10(new_res[:, :, zz]), cmap="jet_r", vmin=0.3, vmax=2.5
    )

    sc = ax.scatter(
        modem_data.data_array["rel_east"],
        modem_data.data_array["rel_north"],
        marker="v",
        c="k",
    )

    ax.set_ylim(-40000, 40000)
    ax.set_xlim(-40000, 40000)
    plt.colorbar(cp)
    print(ii, new_res[:, :, zz].min(), new_res[:, :, zz].max())

plt.show()
