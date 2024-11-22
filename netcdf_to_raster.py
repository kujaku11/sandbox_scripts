# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 12:17:05 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import fiona
import rasterio
import xarray as xr
import rioxarray as rio

# =============================================================================
# netcdf_fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\earth_models\WUS324.r0.0.nc")
netcdf_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\earth_models\WUS256.r0.0.nc"
)
outline = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\cb_2018_us_nation_5m.shp"
)

d = xr.open_dataset(netcdf_fn)
d = d.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude")
d.rio.write_crs("EPSG:4326", inplace=True)

with fiona.open(outline, "r") as shpfile:
    shape = [feature["geometry"] for feature in shpfile]


for index in range(len(d.depth.values)):
    for comp in ["VS", "VP", "XS", "RHO"]:
        z = d.depth.values[index]
        try:
            gtif_fn = netcdf_fn.parent.joinpath(
                "wus256_rasters", f"{comp}_{z:.0f}_km.tif"
            )
            data = d[comp].isel(depth=index)
            clipped_data = data.rio.clip(shape)
            clipped_data.rio.to_raster(gtif_fn)

        except Exception as e:
            print(e)
