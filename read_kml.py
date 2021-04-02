# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 11:44:35 2019

@author: jpeacock
"""

import geopandas as gpd
import fiona

gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"

fn = r"c:\Users\jpeacock\OneDrive - DOI\kml_files\Bureau of Land Management (BLM).kml"

df = gpd.read_file(fn, driver="KML")
