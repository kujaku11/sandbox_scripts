# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 11:07:48 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import rasterio
from rasterio.plot import show

# =============================================================================
with rasterio.open(r"c:\Users\jpeacock\Downloads\musgraves_dem.tiff") as dem:
    elev = dem.read(1)

lines = []
lines.append(f"ncols         {dem.width}")
lines.append(f"nrows         {dem.height}")
lines.append(f"xllcorner     {dem.transform.xoff}")
lines.append(f"yllcorner     {-30.26667}")
lines.append(f"cellsize      {dem.transform.a}")
lines.append("NODATA_value  -9999")

for ii in range(dem.height):
    line = []
    for jj in range(dem.width):
        line.append(f"{elev[ii, jj]:.0f}")
    lines.append(" ".join(line))

with open(r"c:\Users\jpeacock\Downloads\musgraves_dem_b.asc", "w") as fid:
    fid.write("\n".join(lines))
