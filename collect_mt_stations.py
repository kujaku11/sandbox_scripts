# -*- coding: utf-8 -*-
"""
Collection of MT stations

Created on Mon Jan 11 15:36:38 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import xarray as xr
from mtpy.core import mt

# =============================================================================
#
# =============================================================================
class MTCollection:
    """
    Collection of mt data
    """

    def __init__(self, mt_path=None):
        self.mt_path = self.check_path(mt_path)

    def check_path(self, mt_path):
        if mt_path is None:
            return None
        else:
            mt_path = Path(mt_path)
            if not mt_path.exists():
                raise IOError(f"{mt_path} does not exists")
            return mt_path

    def create_mt_file_list(self, mt_path, file_types=[".edi"]):
        """
        Get a list of MT file from a given path
        
        :param mt_path: full path to where the MT transfer functions are stored
        :type mt_path: string or :class:`pathlib.Path`
        
        :param file_types: List of file types to look for given their extension
        :type file_types: list
        
        Currently available file types are or will be:
            - .edi - EDI files
            - .zmm - EMTF output file
            - .j - BIRRP output file
            - .avg - Zonge output file
            
        """
        self.mt_path = self.check_path(mt_path)
        if self.mt_path is None:
            return None

        fn_list = []
        for ext in file_types:
            fn_list += list(self.mt_path.glob(ext))

        return fn_list


edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES")
coordinate_system = {"init": "epsg:4326"}


station_list = []
for fn in edi_path.glob("*.edi"):
    m = mt.MT(fn)
    entry = {}
    entry["fn"] = fn
    entry["ID"] = m.station
    entry["start"] = m.station_metadata.time_period.start
    entry["end"] = m.station_metadata.time_period.end
    entry["latitude"] = m.latitude
    entry["longitude"] = m.longitude
    entry["elevation"] = m.elevation
    entry["acquired_by"] = m.station_metadata.acquired_by.author
    entry["period_min"] = 1.0 / m.Z.freq.max()
    entry["period_max"] = 1.0 / m.Z.freq.min()
    entry["file_date"] = m.station_metadata.provenance.creation_time
    entry["survey"] = m.survey_metadata.survey_id

    # add entry to list to put into data frame
    station_list.append(entry)


# write csv file to querry
sdf = pd.DataFrame(station_list)
duplicates = sdf[sdf.duplicated(["latitude", "longitude"])]
if len(duplicates) > 0:
    print(f"Found {len(sdf)} duplicates, moving oldest to 'Duplicates'")
    dup_path = edi_path.joinpath("Duplicates")
    if not dup_path.exists():
        dup_path.mkdir()
    for ii, row in duplicates.iterrows():
        fn = Path(row.fn)
        new_fn = dup_path.joinpath(Path(row.fn).name)
        try:
            fn.rename(new_fn)
        except FileNotFoundError:
            print(f"Could not find {fn} --> skipping")
sdf = sdf.drop_duplicates(subset=["latitude", "longitude"], keep="first")
sdf.to_csv(edi_path.joinpath("all_mt_stations.csv"), index=False)

# write shape file
geometry_list = []
for ii, row in sdf.iterrows():
    geometry_list.append(Point(row.longitude, row.latitude))

gdf = gpd.GeoDataFrame(sdf, crs=coordinate_system, geometry=geometry_list)
gdf.fn = gdf.fn.astype("str")
gdf.to_file(edi_path.joinpath("all_mt_stations.shp"))
