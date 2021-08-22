# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 12:36:05 2018

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import os
import glob
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import mtpy.core.mt as mt
import fiona

fiona.supported_drivers["KML"] = "rw"
# =============================================================================
# Inputs
# =============================================================================
edi_dir = r"c:\Users\jpeacock\Documents\edi_folders\mono_basin"
save_dir = None
save_fn = r"mb_mt_stations_all"
datum = {"init": "epsg:4326"}

if save_dir is None:
    save_dir = edi_dir
shp_fn = os.path.join(save_dir, save_fn + ".shp")
kml_fn = os.path.join(save_dir, save_fn + ".kml")

# =============================================================================
# make a shape file from edi files
# =============================================================================
edi_list = glob.glob(os.path.join(edi_dir, "*.edi"))

data_arr = np.zeros(
    len(edi_list),
    dtype=[
        ("stationID", "S12"),
        ("latitude", np.float),
        ("longitude", np.float),
        ("elevation", np.float),
        ("ex_len", np.float),
        ("ey_len", np.float),
        ("hx_sensor", "S12"),
        ("hy_sensor", "S12"),
        ("hz_sensor", "S12"),
        ("instrument", "S12"),
        ("start_date", "S24"),
        ("end_date", "S24"),
        ("acq_by", "S24"),
        ("mtype", "S24"),
        ("label", "S24"),
    ],
)

for ii, edi in enumerate(edi_list):
    mt_obj = mt.MT(edi)
    data_arr["stationID"][ii] = mt_obj.station
    data_arr["label"][ii] = mt_obj.station[3:]
    data_arr["latitude"][ii] = mt_obj.lat
    data_arr["longitude"][ii] = mt_obj.lon
    data_arr["elevation"][ii] = mt_obj.elev
    data_arr["ex_len"][ii] = mt_obj.FieldNotes.Electrode_ex.get_length()
    data_arr["ey_len"][ii] = mt_obj.FieldNotes.Electrode_ey.get_length()
    data_arr["hx_sensor"][ii] = mt_obj.FieldNotes.Magnetometer_hx.id
    data_arr["hy_sensor"][ii] = mt_obj.FieldNotes.Magnetometer_hy.id
    data_arr["hz_sensor"][ii] = mt_obj.FieldNotes.Magnetometer_hz.id
    data_arr["instrument"][ii] = mt_obj.FieldNotes.DataLogger.id
    data_arr["mtype"][ii] = "BB"
    #    if mt_obj.Z.freq.min() < 1./3000. and mt_obj.Z.freq.max() > 1./1:
    #        data_arr['instrument'][ii] = 'NIMS + Phoenix_V8'
    #        data_arr['mtype'][ii] = 'BB + LP'
    #    elif mt_obj.Z.freq.min() < 1./3000. and mt_obj.Z.freq.max() <= 10:
    #        data_arr['instrument'][ii] = 'NIMS'
    #        data_arr['mtype'][ii] = 'LP'
    #    else:
    #        data_arr['instrument'][ii] = 'Phoenix_V8'
    #        data_arr['mtype'][ii] = 'BB'
    data_arr["start_date"][ii] = mt_obj.Site.start_date
    data_arr["end_date"][ii] = mt_obj.Site.end_date
    #    if int(mt_obj.station[3:]) >= 900:
    #        data_arr['mtype'][ii] += ' + SGS'
    #        data_arr['acq_by'][ii] = 'SGS'
    #    else:
    data_arr["acq_by"][ii] = "USGS"

### make geopandas data frame with points
gdf = gpd.GeoDataFrame(data_arr, crs=datum,)
gdf["geometry"] = [Point(x["longitude"], x["latitude"]) for x in data_arr]

gdf.to_file(os.path.join(edi_dir, shp_fn))

# write kml file
# gdf = gdf.drop(['lat', 'lon'], axis=1)
gdf = gdf.rename(columns={"station": "name"})
gdf.to_file(kml_fn, driver="KML")
