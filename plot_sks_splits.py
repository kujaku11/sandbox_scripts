# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 14:44:01 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import cm
import contextily as cx

# =============================================================================

df = pd.read_csv(
    r"C:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\papers\2014_walpole_station_averaged_sks_splitting.txt",
    delim_whitespace=True,
)
df = a = df.loc[
    (df.lat > 32) & (df.lat < 48) & (df.lon > -124) & (df.lon < -110)
]

scale = 0.2

# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)

# norm = colors.Normalize(vmin=0.05, vmax=2.5)
# cmap = cm.get_cmap("Spectral_r")

# for row in a.itertuples():
#     if row.tlag > 2.5:
#         continue
#     ax.plot(row.lon, row.lat, marker="o", color="k")
#     ax.plot(
#         [
#             row.lon + scale * row.tlag * np.sin(np.deg2rad(row.fast)),
#             row.lon - scale * row.tlag * np.sin(np.deg2rad(row.fast)),
#         ],
#         [
#             row.lat + scale * row.tlag * np.cos(np.deg2rad(row.fast)),
#             row.lat - scale * row.tlag * np.cos(np.deg2rad(row.fast)),
#         ],
#         lw=4,
#         color=cmap(norm(row.tlag)),
#     )

# cx_kwargs = {
#     "crs": 4326,
#     "source": cx.providers.USGS.USTopo,
#     # "source": cx.providers.Stamen.Terrain,
# }

# cx.add_basemap(
#     ax,
#     **cx_kwargs,
# )
# plt.show()

### create shape file
import fiona


schema = {
    "geometry": "LineString",
    "properties": [("Name", "str"), ("tlag", "float")],
}

with fiona.open(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\sks_splitting_walpole_2014_02.shp",
    mode="w",
    driver="ESRI Shapefile",
    schema=schema,
    crs="EPSG:4326",
) as lines:

    for row in a.itertuples():
        if row.tlag > 2.5:
            continue
        line = [
            (
                row.lon + scale * row.tlag * np.sin(np.deg2rad(row.fast)),
                row.lat + scale * row.tlag * np.cos(np.deg2rad(row.fast)),
            ),
            (
                row.lon - scale * row.tlag * np.sin(np.deg2rad(row.fast)),
                row.lat - scale * row.tlag * np.cos(np.deg2rad(row.fast)),
            ),
        ]

        row_dict = {
            "geometry": {"type": "LineString", "coordinates": line},
            "properties": {"Name": row.sta, "tlag": row.tlag},
        }
        lines.write(row_dict)
