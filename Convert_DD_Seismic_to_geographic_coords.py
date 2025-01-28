# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:05:45 2014

@author: jpeacock
"""

from pathlib import Path
from pyevtk.hl import pointsToVTK
import pandas as pd
import geopandas as gpd
from mtpy.core.mt_location import MTLocation

# ---------------------------------------------------
# sfn = r"c:\Users\jpeacock\Documents\LVEarthquakeLocations_lldm.csv"
# sfn = r"c:\Users\jpeacock\OneDrive - DOI\LV\EarthquakeLocations_DD_lldm.csv"
# sfn = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\cv_eq_new.csv"
# )
# sfn = Path(r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\cl_usgs_eq.csv")
# bbox = ()

# sfn_list = [
#     Path(
#         r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\cl_usgs_eq_mag_1_to_2.csv"
#     ),
#     Path(
#         r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\cl_usgs_eq_mag_2_to_3.csv"
#     ),
#     Path(
#         r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\cl_usgs_eq_mag_3_to_4.csv"
#     ),
#     Path(
#         r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\cl_usgs_eq_mag_4_to_8.csv"
#     ),
# ]

# df_list = []
# for fn in sfn_list:
#     df_list.append(pd.read_csv(fn))

# df = pd.concat(df_list)
# df = pd.read_csv(sfn)
# df = df.loc[
#     (df.lon >= -119.25)
#     & (df.lon <= -118.5)
#     & (df.lat >= 37.5)
#     & (df.lat <= 38.35)
# ]
sfn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\TexDocs\Presentations\mt_shortcourse\2024\yellowstone_model\eq_events.csv"
)

sfn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\utah\anss_eq_query.csv"
)
df = pd.read_csv(sfn)


gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.longitude, df.latitude)
)
gdf.crs = "epsg:4326"
gdf = gdf.to_crs(epsg=32612)

# center = MTLocation(longitude=-118.897992, latitude=37.914380)
# center.utm_epsg = 32611

depth = -1 * gdf.depth.to_numpy(dtype=float)

pointsToVTK(
    sfn.parent.joinpath(f"{sfn.stem}_enzm_km").as_posix(),
    gdf.geometry.x.to_numpy(dtype=float) / 1000,
    gdf.geometry.y.to_numpy(dtype=float) / 1000,
    depth,
    data={
        "mag": gdf.mag.to_numpy(dtype=float),
        "depth": -1 * depth,
    },
)
