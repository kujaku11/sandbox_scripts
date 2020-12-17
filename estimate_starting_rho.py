# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 14:38:14 2018

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import numpy as np
import mtpy.core.z as mtz
import matplotlib.pyplot as plt

dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_07\um_modem_data_z05.dat"

d_obj = modem.Data()
d_obj.read_data_file(dfn)

rho = np.zeros((d_obj.data_array.shape[0], d_obj.period_list.shape[0]))
# det_z = np.linalg.det(d_obj.data_array['z'])
# mean_z = np.mean(det_z[np.nonzero(det_z)], axis=0)
# mean_rho = (.02/(1/d_obj.period_list))*np.abs(mean_z)

for ii, d_arr in enumerate(d_obj.data_array):
    z_obj = mtz.Z(d_arr["z"], freq=1.0 / d_obj.period_list)
    rho[ii, :] = z_obj.res_det

mean_rho = np.apply_along_axis(lambda x: x[np.nonzero(x)].mean(), 0, rho)
median_rho = np.apply_along_axis(lambda x: np.median(x[np.nonzero(x)]), 0, rho)

fig = plt.figure()

ax = fig.add_subplot(1, 1, 1)
(l1,) = ax.loglog(d_obj.period_list, mean_rho, lw=2, color=(0.75, 0.25, 0))
(l2,) = ax.loglog(d_obj.period_list, median_rho, lw=2, color=(0, 0.25, 0.75))

ax.loglog(
    d_obj.period_list,
    np.repeat(mean_rho.mean(), d_obj.period_list.size),
    ls="--",
    lw=2,
    color=(0.75, 0.25, 0),
)
ax.loglog(
    d_obj.period_list,
    np.repeat(np.median(median_rho), d_obj.period_list.size),
    ls="--",
    lw=2,
    color=(0, 0.25, 0.75),
)

ax.set_xlabel("Period (s)", fontdict={"size": 12, "weight": "bold"})
ax.set_ylabel("Resistivity (Ohm-m)", fontdict={"size": 12, "weight": "bold"})

ax.legend(
    [l1, l2],
    [
        "Mean = {0:.1f}".format(mean_rho.mean()),
        "Median = {0:.1f}".format(np.median(median_rho)),
    ],
    loc="upper left",
)
ax.grid(which="both", ls="--", color=(0.75, 0.75, 0.75))

plt.show()
