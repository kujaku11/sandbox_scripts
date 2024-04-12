# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 10:32:55 2023

@author: jpeacock
"""
from pathlib import Path
import numpy as np
from mtpy.modeling import StructuredGrid3D
import rasterio
from rasterio.transform import Affine

fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\BuffaloValley\modem_inv\inv_01\bv_z03_t02_c03_NLCG_147.rho"
)

s = StructuredGrid3D()
s.from_modem(fn)

s.center_point.latitude = 40.275185
s.center_point.longitude = -117.400796
s.center_point.utm_crs = 32611

s.to_raster(500, depth_max=15000)

# pad = 7
# lower_left = s.get_lower_left_corner(pad, pad)

# transform = Affine.translation(
#     lower_left.east,
#     lower_left.north,
# ) * Affine.scale(s.cell_size_east, s.cell_size_north)

# with rasterio.open(
#     fn.parent.joinpath("rasterio_test.tif"),
#     "w",
#     driver="GTiff",
#     height=s.res_model.shape[0] - (pad * 2),
#     width=s.res_model.shape[1] - (pad * 2),
#     count=1,
#     dtype=s.res_model.dtype,
#     crs=s.center_point.utm_crs,
#     transform=transform,
# ) as dataset:
#     dataset.write(
#         np.log10(s.res_model[pad:-pad, pad:-pad, 30]),
#         1,
#     )
