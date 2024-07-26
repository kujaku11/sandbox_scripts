# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 10:45:41 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import interpolate
import geopandas as gpd
from pyevtk.hl import gridToVTK, pointsToVTK


# =============================================================================
fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\2022_qi_seismic_model_ClearLake\ModelinGEOS"
)
units = "m"
epsg = 32610
df = pd.read_csv(
    fn,
    delim_whitespace=True,
    header=None,
    usecols=[0, 1, 2, 3, 5],
    names=["lon", "lat", "z", "vp", "moho"],
)

df = df.groupby("moho", as_index=False).first()

gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.lon, df.lat), crs=4326
)
utm_gdf = gdf.to_crs(epsg=32610)
utm_gdf["easting"] = utm_gdf.geometry.x
utm_gdf["northing"] = utm_gdf.geometry.y

scale = 1
if units in ["km"]:
    scale = 1000

pointsToVTK(
    Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\seismic")
    .joinpath(f"2024_li_moho_depth_{epsg}_{units}")
    .as_posix(),
    utm_gdf.easting.to_numpy() / scale,
    utm_gdf.northing.to_numpy() / scale,
    utm_gdf.moho.to_numpy() * -1000 / scale,
    data={"moho": utm_gdf.moho.to_numpy()},
)

# dx = int((utm_gdf.easting.max() - utm_gdf.easting.min()) / 2)
# dy = int((utm_gdf.northing.max() - utm_gdf.northing.min()) / 2)

# x = np.linspace(utm_gdf.easting.min(), utm_gdf.easting.max(), dx + 1)
# y = np.linspace(utm_gdf.northing.min(), utm_gdf.northing.max(), dy + 1)
# depth = np.append(utm_gdf.z.unique() * 1000 * -1, [36000])

# # interpolate onto a regular grid
# new_vp = np.zeros((x.size - 1, y.size - 1, depth.size - 1))

# for index, z in enumerate(utm_gdf.z.unique()):
#     zdf = utm_gdf[utm_gdf.z == z]
#     grid_x = zdf.easting.array.reshape((ny, nx))
#     grid_y = zdf.northing.array.reshape((ny, nx))
#     velocity = zdf.vp.array.reshape((ny, nx))

#     new_vp[:, :, index] = interpolate.griddata(
#         (grid_x.ravel(), grid_y.ravel()),
#         velocity.ravel(),
#         (x[:-1, None], y[None, :-1]),
#     )

# # estimate vp/vs
# cell_data = {"vp": new_vp}

# gridToVTK(
#     fn.parent.joinpath("2024_li_vp").as_posix(),
#     x,
#     y,
#     depth,
#     cellData=cell_data,
# )
