# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 13:41:45 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import geopandas as gpd
from mtpy import MT
from mt_metadata.utils.mttime import MTime

# =============================================================================
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\EDI_Files_birrp_phase_02\final_edi"
)

gpd_list = []
x = []
y = []
for fn in edi_path.glob("*.edi"):
    m = MT()
    m.read(fn)
    m.utm_epsg = 32610

    item = {}
    item["ID"] = m.station
    item["start"] = m.station_metadata.time_period.start
    item["end"] = (
        m.station_metadata.time_period._start_dt + 16 * 3600
    ).isoformat()
    item["latitude"] = m.latitude
    item["longitude"] = m.longitude
    item["elevation"] = m.elevation
    item["easting"] = m.east
    item["northing"] = m.north
    item["utm_zone"] = m.utm_zone
    item["acquired_b"] = "U.S. Geological Survey"
    item["period_min"] = m.period.min()
    item["period_max"] = m.period.max()
    item["n_periods"] = m.period.size
    item["survey"] = "UM2020"
    item["fn"] = fn.name
    item["file_date"] = MTime(fn.stat().st_mtime).isoformat()
    gpd_list.append(item)
    x.append(m.longitude)
    y.append(m.latitude)

gdf = gpd.GeoDataFrame(gpd_list, geometry=gpd.points_from_xy(x, y))
gdf.set_crs(epsg=4326, inplace=True)

gdf.to_file(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\archive\ctuir_phase_02_mt_stations_02.shp"
)
