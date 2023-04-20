# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 12:01:01 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================

import numpy as np
import pandas as pd
from pyevtk.hl import gridToVTK
from mtpy.core.mt_location import MTLocation

# =============================================================================


sfn = r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\inv_all_01\LV_tomoModel.csv"

bbox = ()

df = pd.read_csv(sfn)
df = df.loc[
    (df.longitude >= -119.25)
    & (df.longitude <= -118.5)
    & (df.latitude >= 37.5)
    & (df.latitude <= 38.35)
]

sw_corner = MTLocation(latitude=df.latitude.min(), longitude=df.longitude.min())
sw_corner.utm_epsg = 32611
dx = 500
ny = df.longitude.unique().size
nx = df.latitude.unique().size
nz = df.depth.unique().size

### rememeber x, y, z must be nx + 1, ny + 1, nz + 1 for gridToVTK

y = np.arange(
    sw_corner.east, sw_corner.east + dx * (df.longitude.unique().size + 1), dx
)
x = np.arange(
    sw_corner.north, sw_corner.north + dx * (df.latitude.unique().size + 1), dx
)
z = df.depth.unique()
z = np.append(z, np.array([z[-1] + (dx / 1000)])) + 2

center = MTLocation(longitude=-118.897992, latitude=37.914380)
center.utm_epsg = 32611

y -= center.east
x -= center.north

x /= 1000
y /= 1000

vs = np.zeros((nx, ny, nz))
vp = np.zeros((nx, ny, nz))

zcount = 0
for ii in range(nx):
    for jj in range(ny):
        vs[ii, jj, :] = df.vs[zcount * nz : (zcount + 1) * nz]
        vp[ii, jj, :] = df.vp[zcount * nz : (zcount + 1) * nz]
        # vs[ii, (ny - 1) - jj, :] = df.vs[zcount * nz : (zcount + 1) * nz]
        # vp[ii, (ny - 1) - jj, :] = df.vp[zcount * nz : (zcount + 1) * nz]
        zcount += 1

# look at percent difference
vp_percent = (1 - vp[:, :] / vp.mean(axis=(0, 1))) * 100
vs_percent = (1 - vs[:, :] / vs.mean(axis=(0, 1))) * 100

gridToVTK(
    r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\inv_all_01\LV_tomoModel",
    x,
    y,
    z,
    cellData={
        "vp": vp,
        "vs": vs,
        "vp/vs": (vp / vs),
        "vp_percent": vp_percent,
        "vs_percent": vs_percent,
    },
)
