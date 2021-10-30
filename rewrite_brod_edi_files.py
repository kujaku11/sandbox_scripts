# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 12:52:25 2021

@author: jpeacock
"""
from pathlib import Path
from mtpy.core.mt import MT

epath = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES")
fn_list = list(epath.glob("USA-Utah*"))

chars = 280

key_dict = {
    "latitude": "location.latitude",
    "longitude": "location.longitude",
    "elevation": "location.elevation",
    "declination": "location.declination.value",
    "declination.epoch": "location.declination.epoch",
    "start": "time_period.start",
    "end": "time_period.end",
}
# "runlist": "run_list"}

for fn in fn_list:
    m = MT(fn)

    find = m.station_metadata.comments.find("SITE LATITUDE")
    lines = m.station_metadata.comments[find : find + chars].split("\n")
    attr_dict = {}
    for line in lines:
        if line.count("=") == 0:
            continue
        if line.count("=") > 1:
            key, value = line.split(" ")
            attr, units, value = value.split("=")
            attr_dict[key.lower()] = value
            attr_dict[f"{key.lower()}.{attr}"] = units
        else:
            key, value = line.split("=")
            key = key.replace("SITE", "").lower().strip().replace(" ", "_")
            value = value.replace(r"UTC/GMT", "").replace('"', "")
            attr_dict[key] = value

    for brod_key, mt_key in key_dict.items():
        value = attr_dict[brod_key]
        m.station_metadata.set_attr_from_name(mt_key, value)

    m.write_mt_file(fn.name, save_dir=fn.parent)
