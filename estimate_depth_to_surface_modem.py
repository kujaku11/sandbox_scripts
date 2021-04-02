# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 12:01:06 2019

@author: jpeacock
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
from mtpy.modeling import modem

# =============================================================================
# Parameters
# =============================================================================
mfn = r"c:\Users\jpeacock\Documents\Geysers\modem_inv\inv03\gz_err03_cov02_NLCG_057.rho"
dfn = r"c:\Users\jpeacock\Documents\Geysers\modem_inv\inv03\gz_data_err03_tec_edit.dat"

rho = 85
pad = 8
z0 = -1260
z_index = 42
d_max = 4
cmap = "RdBu"
# =============================================================================
#
# =============================================================================
m_obj = modem.Model()
m_obj.read_model_file(mfn)

depth = np.zeros(
    (m_obj.nodes_north[pad:-pad].shape[0], m_obj.nodes_east[pad:-pad].shape[0])
)

res = m_obj.res_model[pad:-pad, pad:-pad, z_index:]
for nn in range(res.shape[0]):
    for ee in range(res.shape[1]):
        for zz in range(res.shape[2]):
            try:
                d_index = np.where(res[nn, ee, :] > rho)[0][0]
                depth[nn, ee] = m_obj.grid_z[z_index + d_index] + z0
            except IndexError:
                d_index = 0
                depth[nn, ee] = np.nan

# =============================================================================
# Plot
# =============================================================================
d_obj = modem.Data()
d_obj.read_data_file(dfn)

x, y = np.meshgrid(m_obj.grid_east[pad : -pad - 1], m_obj.grid_north[pad : -pad - 1])

fig = plt.figure(1, dpi=200)
fig.clf()
ax = fig.add_subplot(1, 1, 1, aspect="equal")

depth[np.where(depth / 1000.0 > d_max)] = np.nan
im = ax.pcolormesh(
    x / 1000.0, y / 1000.0, depth / 1000.0, vmin=0, vmax=d_max, cmap=cmap
)
q = ax.contour(
    x / 1000.0, y / 1000.0, depth / 1000.0, 10, vmin=0.05, vmax=d_max, cmap=cmap
)
cb = plt.colorbar(im, shrink=0.75)
cb.set_label("Depth bmsl (km)", fontdict={"size": 13, "weight": "bold"})

ax.scatter(
    d_obj.station_locations.rel_east / 1000.0,
    d_obj.station_locations.rel_north / 1000.0,
    marker="v",
    s=20,
    c="k",
    zorder=30,
)

ax.set_xlabel("Easting (km)", fontdict={"size": 13, "weight": "bold"})
ax.set_ylabel("Northing (km)", fontdict={"size": 13, "weight": "bold"})
ax.xaxis.set_minor_locator(MultipleLocator(0.25))
ax.yaxis.set_minor_locator(MultipleLocator(0.25))
ax.set_axisbelow(True)
ax.grid()
fig.tight_layout()

plt.show

fig.savefig(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\jvgr\gz_depth_{0:.0f}ohmm.pdf".format(
        rho
    ),
    dpi=300,
)
