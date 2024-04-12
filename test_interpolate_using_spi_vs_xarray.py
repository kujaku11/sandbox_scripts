# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 11:57:23 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np
import xarray as xr
from scipy import interpolate as spi
from matplotlib import pyplot as plt

# =============================================================================
period = np.array(
    [
        2.00000e-03,
        3.63516e-03,
        6.60718e-03,
        1.20091e-02,
        2.18274e-02,
        3.96730e-02,
        7.21087e-02,
        1.31063e-01,
        2.38218e-01,
        4.32979e-01,
        7.86973e-01,
        1.43038e00,
        2.59984e00,
        4.72540e00,
        8.58879e00,
        1.56108e01,
        2.83738e01,
        5.15716e01,
        9.37354e01,
        1.70371e02,
        3.09663e02,
        5.62837e02,
        1.02300e03,
    ]
)
zxx = np.array(
    [
        -127.9288 - 17.42628j,
        -127.9288 - 17.42628j,
        -110.1287 - 36.98663j,
        -28.94418 - 73.92679j,
        -39.83527 - 39.56024j,
        -39.2504 - 26.18195j,
        -31.39731 - 20.08989j,
        -26.42417 - 13.90437j,
        -24.82012 - 10.85238j,
        -24.66433 - 11.19993j,
        -23.41857 - 13.41101j,
        -17.60641 - 13.67275j,
        -10.94526 - 11.26471j,
        -6.292439 - 7.463986j,
        -3.485051 - 4.802622j,
        -3.297289 - 2.730986j,
        -2.840465 - 1.330059j,
        -2.741103 - 0.8539506j,
        -2.603723 - 0.7500773j,
        -2.320917 - 0.3055995j,
        -2.274778 - 0.5205574j,
        -2.0463 - 0.5892314j,
        -1.890979 - 0.6137499j,
    ]
)
# zxy
# zxx = np.array(
#     [
#         -4.522871e02 - 5.035564e02j,
#         -2.960298e02 - 3.201417e02j,
#         -1.937144e02 - 2.083304e02j,
#         -1.042694e02 - 1.202408e02j,
#         -5.414659e01 - 7.087757e01j,
#         -3.030850e01 - 4.789075e01j,
#         -2.056084e01 - 3.188444e01j,
#         -1.538068e01 - 2.060503e01j,
#         -1.289389e01 - 1.443078e01j,
#         -1.323090e01 - 1.146407e01j,
#         -1.487640e01 - 1.068844e01j,
#         -1.078277e01 - 7.753179e00j,
#         -7.566246e00 - 5.989438e00j,
#         -5.083587e00 - 4.369552e00j,
#         -3.016759e00 - 2.967777e00j,
#         -1.677137e00 - 2.059030e00j,
#         -1.013575e00 - 1.208373e00j,
#         -7.781579e-01 - 7.944608e-01j,
#         -6.466979e-01 - 5.610001e-01j,
#         -5.839485e-01 - 3.738069e-01j,
#         -4.803875e-01 - 3.190335e-01j,
#         -3.819702e-01 - 2.442666e-01j,
#         -3.167354e-01 - 1.921062e-01j,
#     ]
# )

index_00 = 9
index_01 = 14
## edit the zxx component
zxx_edit = zxx.copy()
zxx_edit[index_00:index_01] = np.nan + 1j * np.nan

nz = np.nonzero(np.nan_to_num(zxx_edit))

kind = "slinear"
interp_zxx_slinear = spi.interp1d(period[nz], zxx_edit[nz], kind=kind)
interp_zxx_pchip = spi.PchipInterpolator(period[nz], zxx_edit[nz])

zxx_interp_slinear = interp_zxx_slinear(period)
zxx_interp_pchip = interp_zxx_pchip(period)

# xarray method
da_zxx = xr.DataArray(zxx_edit, coords=[("period", period)])
da_drop_na = da_zxx.interpolate_na(dim="period", method="pchip")
da_interp = da_drop_na.interp(period=period, method="slinear")


fig = plt.figure(figsize=[8, 4])
axr = fig.add_subplot(1, 1, 1)

axr.loglog(period, abs(zxx) ** 2 * period, "k", marker="s")
axr.loglog(period, abs(zxx_interp_slinear) ** 2 * period, "b", marker="o")
axr.loglog(period, abs(zxx_interp_pchip) ** 2 * period, "r", marker="o")
axr.loglog(period, abs(da_interp.data) ** 2 * period, "g", marker="o")

axr.fill_betweenx(
    [1, 10000],
    period[index_00],
    period[index_01],
)

plt.legend(["data", "slinear", "pchip", "xarray"])
plt.show()
