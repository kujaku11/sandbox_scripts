# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import xarray as xr
import rioxarray

tf = rioxarray.open_rasterio(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_03\conductance_maps\conductance_30000m_to_60000m_depth_utm_32611.tif"
)
a = tf.rio.reproject("EPSG:4326")
b = xr.DataArray(
    a.data[0],
    coords={"y": a.y, "x": a.x, "spatial_ref": a.spatial_ref},
    dims=["y", "x"],
    name="data",
)
b.to_netcdf(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_03\conductance_maps\conductance_30000m_to_60000m_depth_utm_32611.nc"
)
