# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 12:03:31 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================

import numpy as np
import xarray as xr
from mtpy import MT

import matplotlib.pyplot as plt

# =============================================================================
period = np.array(
    [
        1.30310002e-03,
        1.84547539e-03,
        2.61359808e-03,
        3.70142801e-03,
        5.24203525e-03,
        7.42387191e-03,
        1.05138309e-02,
        1.48898907e-02,
        2.10873525e-02,
        2.98643234e-02,
        4.22944216e-02,
        5.98981731e-02,
        8.48290102e-02,
        1.20136441e-01,
        1.70139555e-01,
        2.40954972e-01,
        3.41245101e-01,
        4.83277861e-01,
        6.84427562e-01,
        9.69299381e-01,
        1.37274088e00,
        1.94410239e00,
        2.75327516e00,
        3.89924203e00,
        5.52218316e00,
        7.82062000e00,
        1.10757168e01,
        1.56856446e01,
        2.22143139e01,
        3.14603419e01,
        4.45547422e01,
        6.30992855e01,
        8.93624703e01,
        1.26556839e02,
        1.79232251e02,
        2.53832168e02,
        3.59482058e02,
        5.09105608e02,
        7.21004966e02,
        1.02110137e03,
        1.44610358e03,
        2.04800021e03,
    ]
)

z = np.array(
    [
        6.683830e02 + 4.078443e02j,
        3.104369e02 + 2.207070e02j,
        2.157676e02 + 1.775154e02j,
        1.609542e02 + 1.728643e02j,
        1.466181e02 + 1.529377e02j,
        1.173698e02 + 1.275895e02j,
        9.716396e01 + 1.091940e02j,
        7.469862e01 + 8.958256e01j,
        5.838714e01 + 7.552380e01j,
        4.564222e01 + 6.426823e01j,
        3.708196e01 + 5.171494e01j,
        3.148808e01 + 4.263437e01j,
        2.669069e01 + 3.507716e01j,
        2.155636e01 + 2.827576e01j,
        1.771850e01 + 2.313252e01j,
        1.466339e01 + 1.852517e01j,
        1.213034e01 + 1.480061e01j,
        1.012260e01 + 1.187252e01j,
        8.545071e00 + 9.637905e00j,
        7.273314e00 + 7.853160e00j,
        6.233394e00 + 6.405924e00j,
        5.393272e00 + 5.264520e00j,
        4.704277e00 + 4.413923e00j,
        4.130451e00 + 3.842178e00j,
        3.556035e00 + 3.353422e00j,
        3.119275e00 + 3.138219e00j,
        2.424141e00 + 2.920021e00j,
        1.807002e00 + 2.693094e00j,
        1.199939e00 + 2.365704e00j,
        6.207659e-01 + 1.903496e00j,
        2.847894e-01 + 1.456216e00j,
        8.327586e-02 + 9.994997e-01j,
        3.528793e-02 + 6.559722e-01j,
        5.815702e-03 + 4.106243e-01j,
        1.201863e-02 + 2.769342e-01j,
        2.927503e-02 + 1.790282e-01j,
        4.224342e-02 + 1.265575e-01j,
        6.705845e-02 + 1.019352e-01j,
        5.395244e-02 + 6.493036e-02j,
        6.719173e-02 + 2.249362e-02j,
        2.359327e-02 + 2.964848e-02j,
        1.698321e-02 + 2.066148e-02j,
    ]
)

z[[3, 7, 8, 9, 33]] = np.nan + 1j * np.nan

da = xr.DataArray(z, coords={"period": period}, dims=["period"])

fig = plt.figure()
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
ax1.loglog(
    period,
    da.data.real,
    ls="-",
    marker="s",
    color="k",
    mfc="k",
    mec="k",
    ms=10,
)
ax2.loglog(
    period,
    da.data.imag,
    ls="-",
    marker="s",
    color="k",
    mfc="k",
    mec="k",
    ms=10,
)

line_list = []
label_list = []
methods = ["nearest", "quadratic", "cubic"]
new_period = np.logspace(-3, 3, 25)
for na_method in methods[-1:]:
    no_na_da = da.interpolate_na(dim="period", method=na_method)
    (l1,) = ax1.loglog(period, no_na_da.data.real, ls="None", marker="o")
    (l1,) = ax2.loglog(period, no_na_da.data.imag, ls="None", marker="o")
    line_list.append(l1)
    label_list.append(na_method)

    for interp_method in methods:
        interp_da = no_na_da.interp(period=new_period, method=interp_method)
        (l1,) = ax1.loglog(new_period, interp_da.data.real, ls="--", marker="x")
        (l1,) = ax2.loglog(new_period, interp_da.data.imag, ls="--", marker="x")
        line_list.append(l1)
        label_list.append(f"{na_method} + {interp_method}")
ax1.legend(line_list, label_list)


# interp_da = no_na_da.interp(period=np.logspace(-3, 3, 20), method="cubic")


m = MT()
m.read(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\BuffaloValley\EDI_Files_aurora\edited\GeographicNorth\bv100.edi"
)
