# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 13:45:39 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
from pathlib import Path
from mtpy.core import mt_collection

mc = mt_collection.MTCollection()
mc.from_csv(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\all_mt_stations.csv")

new_tf_dir = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES")
new_fn_list = list(new_tf_dir.glob("um2*"))

mc.mt_df = mc.add_stations_from_file_list(new_fn_list)
mc.to_csv(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\all_mt_stations_02.csv")
