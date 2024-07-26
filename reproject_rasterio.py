# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 16:09:55 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

# =============================================================================

geotiff_file = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\SAGE\modem_inv\tiffs\Gravity_CBA_2670_All_400m_epsg_32613.tif"
)
# dst_crs = "EPSG:32613"
dst_crs = 4326

with rasterio.open(geotiff_file) as src:
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds
    )
    kwargs = src.meta.copy()
    kwargs.update(
        {
            "crs": dst_crs,
            "transform": transform,
            "width": width,
            "height": height,
        }
    )

    with rasterio.open(
        geotiff_file.parent.joinpath(f"{geotiff_file.stem}_epsg_{dst_crs}.tif"),
        "w",
        **kwargs,
    ) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest,
            )
