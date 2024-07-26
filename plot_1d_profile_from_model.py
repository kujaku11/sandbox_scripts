# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 08:23:34 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
from mtpy import MTData
from mtpy.modeling import StructuredGrid3D

from matplotlib import pyplot as plt

# =============================================================================

d = MTData()
d.from_modem(
    r"c:\Users\jpeacock\OneDrive - DOI\SAGE\modem_inv\VC_2024_ZT_resp_cull.dat"
)
d._center_lat = 0
d._center_lon = 0
d.utm_crs = 32613

s = StructuredGrid3D()
s.from_modem(
    r"c:\Users\jpeacock\OneDrive - DOI\SAGE\modem_inv\VC_2024_ZT_NLCG_111.rho"
)
s.station_locations = d.station_locations
s.center_point = d.center_point

# pick station
station = "V2406"

if station not in s.station_locations.station.unique():
    raise ValueError(f"{station} not found.")

sdf = s.station_locations[s.station_locations.station == station]

east_index = np.where((s.grid_east <= float(sdf.model_east)))[0][-1]
north_index = np.where((s.grid_north <= float(sdf.model_north)))[0][-1]

res_1d = s.res_model[north_index, east_index, :]
res_1d[np.where(res_1d > 10000)] = np.nan

fig = plt.figure(3, dpi=150)

ax = fig.add_subplot(1, 1, 1)
ax.plot(res_1d, s.grid_z[0:-1] / 1000, ls="--", marker="s", ms=4)
ax.set_xscale("log")
ax.set_yscale("symlog")

ax.set_xlabel(
    "Resistivity ($\Omega \cdot m$)", fontdict={"size": 12, "weight": "bold"}
)
ax.set_ylabel("Depth (km)", fontdict={"size": 12, "weight": "bold"})

ax.set_ylim(50, 0)
ax.grid(which="major", color="k", lw=0.75, ls="--")
ax.grid(which="minor", color=(0.65, 0.65, 0.65), lw=0.5, ls=":")
fig.suptitle(station, fontdict={"size": 14, "weight": "bold"})
fig.tight_layout()

plt.show()
