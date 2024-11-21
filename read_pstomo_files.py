# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 14:55:38 2024

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
from pyevtk.hl import gridToVTK
from mtpy.gis import raster_tools
from mtpy.core import MTLocation


# =============================================================================
def read_pstomo_1d(fn, nz=150):
    df = pd.read_csv(fn, delimiter="\s+", names=["depth", "vp"])

    d = np.linspace(df.depth.min(), df.depth.max(), nz)
    v = np.zeros_like(d)
    for ii, dd in enumerate(d):
        v[ii] = df.loc[(df.depth <= dd)].vp.array[-1]

    return v


def read_pstomo_velocity_file(
    fn, nx=120, ny=174, nz=150, utm_epsg=32610, units="m"
):
    df = pd.read_csv(
        fn,
        names=["longitude", "latitude", "z", "vp"],
        delimiter="\s+",
    )

    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude)
    )
    gdf.crs = 4326

    gdf_utm = gdf.to_crs(epsg=32610)
    gdf_utm["easting"] = gdf_utm.geometry.x
    gdf_utm["northing"] = gdf_utm.geometry.y

    x = np.linspace(gdf_utm.easting.min(), gdf_utm.easting.max(), nx + 1)
    y = np.linspace(gdf_utm.northing.min(), gdf_utm.northing.max(), ny + 1)
    depth = np.append(gdf_utm.z.unique() * 1000 * -1, [-80000])

    # interpolate onto a regular grid
    new_vp = np.zeros((nx, ny, nz))

    for index, z in enumerate(gdf_utm.z.unique()):
        zdf = gdf_utm[gdf_utm.z == z]
        grid_x = zdf.easting.array.reshape((ny, nx))
        grid_y = zdf.northing.array.reshape((ny, nx))
        velocity = zdf.vp.array.reshape((ny, nx))

        new_vp[:, :, index] = interpolate.griddata(
            (grid_x.ravel(), grid_y.ravel()),
            velocity.ravel(),
            (x[:-1, None], y[None, :-1]),
        )

    if units in ["km", "kilometers"]:
        scale = 1000
    else:
        scale = 1
    return (x / scale), (y / scale), (depth / scale), new_vp


# =============================================================================
#
# =============================================================================
fn_dict = {
    "vp": Path(
        r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\seismic\2024_furlong_pwave_model.llzv"
    ),
    "vs": Path(
        r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\seismic\2024_furlong_swave_model.llzv"
    ),
}

epsg = 32610
units = "m"
cell_data = {}
for key, fn in fn_dict.items():
    x, y, depth, velocity = read_pstomo_velocity_file(
        fn, utm_epsg=epsg, units=units
    )
    cell_data[key] = velocity

# estimate vp/vs
cell_data["vpvs"] = cell_data["vp"] / cell_data["vs"]

# read 1D model
vp1d = read_pstomo_1d(
    Path(
        r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\seismic\2024_furlong_starting_1d_vel_p.txt"
    )
)

cell_data["dvp"] = cell_data["vp"] - vp1d

lower_left = MTLocation()
lower_left.utm_crs = epsg
lower_left.east = x.min()
lower_left.north = y.min()

index = np.where(depth < 30000)[0][-1]


raster_tools.array2raster(^M
    r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\seismic\dvp_30km.tif",^M
    cell_data["dvp"][:, :, 60].T,^M
    lower_left,^M
    3000,
    3000,
    lower_left.utm_epsg
    )

# gridToVTK(
#     fn.parent.joinpath(f"2024_furlong_vp_{epsg}_{units}").as_posix(),
#     x,
#     y,
#     depth,
#     cellData=cell_data,
# )
