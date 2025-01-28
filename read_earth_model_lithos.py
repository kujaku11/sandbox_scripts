# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 12:36:37 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
import xarray as xr
import rioxarray

# =============================================================================

ds = xr.load_dataset(
    r"c:\Users\jpeacock\OneDrive - DOI\earth_models\LITHO1.0.nc"
)

lon_min = -126.5
lon_max = -110
lat_min = 32
lat_max = 45

clip = ds.where(
    (
        (ds.longitude >= lon_min)
        & (ds.longitude <= lon_max)
        & (ds.latitude >= lat_min)
        & (ds.latitude <= lat_max)
    ),
    drop=True,
)
clip = clip.rio.write_crs("EPSG:4326")

clip = clip.interp(
    longitude=np.linspace(
        clip.longitude.min(),
        clip.longitude.max(),
        int((clip.longitude.max() - clip.longitude.min()) / 0.10),
    ),
    latitude=np.linspace(
        clip.latitude.min(),
        clip.latitude.max(),
        int((clip.latitude.max() - clip.latitude.min()) / 0.10),
    ),
    method="cubic",
)


# b = xr.DataArray(
#     clip.data[0],
#     coords={"y": a.y, "x": a.x, "spatial_ref": a.spatial_ref},
#     dims=["y", "x"],
#     name="data",
# )

clip.to_netcdf(
    r"c:\Users\jpeacock\OneDrive - DOI\earth_models\LITHO_gb_interp.nc"
)
