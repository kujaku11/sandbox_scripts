# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 10:49:31 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path

import fiona
import rasterio
import rasterio.mask
from rasterio.warp import calculate_default_transform, reproject, Resampling

# =============================================================================
conductance_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_03"
)
shapefile_clip = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\ArcGIS\cb_2018_us_nation_5m.shp"
)


def clip_raster(raster_fn, shape_fn):
    with fiona.open(shape_fn, "r") as shapefile:
        shapes = [feature["geometry"] for feature in shapefile]

    with rasterio.open(raster_fn) as src:
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta

    out_meta.update(
        {
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
        }
    )

    with rasterio.open(
        raster_fn.parent.joinpath(f"{raster_fn.stem}_masked.tif"),
        "w",
        **out_meta,
    ) as dest:
        dest.write(out_image)


# dst_crs = "EPSG:32613"
dst_crs = 4326


def reproject_raster(geotiff_file, dst_src):
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

        projected_fn = geotiff_file.parent.joinpath(
            f"{geotiff_file.stem}_epsg_{dst_crs}.tif"
        )
        with rasterio.open(
            projected_fn,
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
        return projected_fn


datum_crs = 4326
for fn in conductance_path.glob("conductance*"):
    projected_fn = reproject_raster(fn, datum_crs)
    clip_raster(projected_fn, shapefile_clip)
