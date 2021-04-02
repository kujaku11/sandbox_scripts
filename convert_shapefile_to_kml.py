# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:05:25 2019

@author: jpeacock
"""

import geopandas as gpd
import fiona

fiona.drvsupport.supported_drivers["KML"] = "rw"
fiona.drvsupport.supported_drivers["kml"] = "rw"

shp_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\gis\WDPA_Nov2019_protected_area_76526-shapefile-polygons.shp"

shp_obj = gpd.read_file(shp_fn)
shp_obj.to_file(shp_fn[:-4] + ".kml", driver="kml")
