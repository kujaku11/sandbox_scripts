# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 08:22:47 2022

@author: jpeacock
"""

import geopandas as gpd
import numpy as np

from pyevtk.hl import pointsToVTK
import pyproj


def project_points(x, y, initial_crs, final_crs):
    project = pyproj.Transformer.from_crs(initial_crs, final_crs)

    new_x, new_y = project.transform(x, y)
    if isinstance(x, (float, int)):
        if new_x == np.inf and new_y == np.inf:
            new_x, new_y = project.transform(y, x)
    else:
        if new_x[0] == np.inf and new_y[0] == np.inf:
            new_x, new_y = project.transform(y, x)
    return new_x, new_y


def shape_to_points(
    shp_fn,
    final_epsg,
    model_east,
    model_north,
    model_depth=0,
    x="latitude",
    y="longitude",
):
    gdf = gpd.read_file(shp_fn)

    initial_crs = gdf.crs
    final_crs = pyproj.CRS(f"EPSG:{final_epsg}")

    if x == None or y == None:
        new_x, new_y = project_points(
            gdf.geometry.x.to_numpy(),
            gdf.geometry.y.to_numpy(),
            initial_crs,
            final_crs,
        )
    else:
        new_x, new_y = project_points(
            gdf[x].to_numpy(), gdf[y].to_numpy(), initial_crs, final_crs
        )
    new_x -= model_east
    new_y -= model_north
    depth = np.zeros(gdf.shape[0]) - model_depth

    return new_x / 1000, new_y / 1000, depth / 1000


def shp_to_vtk(
    shp_fn,
    vtk_fn,
    final_epsg,
    model_center,
    model_depth=0,
    x="latitude",
    y="longitude",
    coordinate_system="enz-",
):
    if model_center:
        model_east, model_north = project_points(
            model_center[0],
            model_center[1],
            pyproj.CRS("EPSG:4326"),
            pyproj.CRS(f"EPSG:{final_epsg}"),
        )
    else:
        model_east = 0
        model_north = 0

    x, y, z = shape_to_points(
        shp_fn,
        final_epsg,
        model_east,
        model_north,
        model_depth=model_depth,
        x=x,
        y=y,
    )

    if "-" in coordinate_system:
        pointsToVTK(vtk_fn, x, y, -1 * z)
    else:
        pointsToVTK(vtk_fn, y, x, z)


# =============================================================================
#
# =============================================================================
# Great Basin
model_center = (38.615252, -119.015192)

# # geothermal
# shp_to_vtk(
#     r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\geothermal\area_geothermal_operating_sites_10_26_15.shp",
#     r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\active_geothermal",
#     32611,
#     model_center)

# volcanoes
shp_to_vtk(
    r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\CaliforniaVolcano_locations_threatRank.shp",
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\volcanoes_enzm",
    32611,
    None,
    x="Xcoord",
    y="Ycoord",
)

# gold
# shp_to_vtk(
#     r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\minerals\gb_gold.shp",
#     r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gold",
#     32611,
#     model_center,
#     x=None,
#     y=None,
# )
