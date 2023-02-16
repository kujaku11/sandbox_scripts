# -*- coding: utf-8 -*-
"""
Read in NetCDF Earth models from IRIS: http://ds.iris.edu/spud/earthmodel

All coordinates of these files are latitude and longitude in what is assumed
to be WGS84

Output a vtk file in UTM coordinates with a user defined shift to line up
with existing models. 

@author J. Peacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import xarray as xr
import numpy as np

# from scipy import interpolate

import mtpy.utils.gis_tools as gis_tools
from pyevtk.hl import gridToVTK, pointsToVTK
import pyproj as proj

# import mtpy.utils.array2raster as a2r
# =============================================================================
# Useful functions
# =============================================================================


def project_grid(
    latitude,
    longitude,
    utm_zone=None,
    epsg=None,
    shift_east=0.0,
    shift_north=0.0,
    points=False,
    pyproj_str=None,
):
    """
    Project the model grid into UTM coordinates

    :param latitude: latitude array
    :type latitude: np.ndarray
    :param longitude: longitude array
    :type longitude: np.ndarray
    :param utm_zone: Desired UTM zone, defaults to None
    :type utm_zone: string, optional
    :param epsg: desired UTM zone, defaults to None
    :type epsg: int, optional
    :param shift_east: meters to shift the grid east, defaults to 0.0
    :type shift_east: float, optional
    :param shift_north: meters to shift the grid north, defaults to 0.0
    :type shift_north: float, optional
    :return: east, north, utm_zone
    :rtype: float, float, string

    """
    if pyproj_str is None:
        lower_left = gis_tools.project_point_ll2utm(
            latitude.min(), longitude.min(), utm_zone=utm_zone, epsg=epsg
        )
        lower_right = gis_tools.project_point_ll2utm(
            latitude.min(), longitude.max(), utm_zone=utm_zone, epsg=epsg
        )
        upper_right = gis_tools.project_point_ll2utm(
            latitude.max(), longitude.max(), utm_zone=utm_zone, epsg=epsg
        )
        upper_left = gis_tools.project_point_ll2utm(
            latitude.max(), longitude.min(), utm_zone=utm_zone, epsg=epsg
        )

        utm_zone = lower_left[-1]
    else:
        default_proj = proj.Proj(init="epsg:4326")
        custom_proj = proj.Proj(pyproj_str)
        lower_left = proj.transform(
            default_proj, custom_proj, longitude.min(), latitude.min()
        )
        lower_right = proj.transform(
            default_proj, custom_proj, longitude.max(), latitude.min()
        )
        upper_right = proj.transform(
            default_proj, custom_proj, longitude.max(), latitude.max()
        )
        upper_left = proj.transform(
            default_proj, custom_proj, longitude.min(), latitude.max()
        )
        utm_zone = "custom"

    # get corners
    # not that since we have to have a regular grid we cannot take into account
    # distortion of the cells caused by the given projection.  So we will look
    # for the mean location.
    left = np.array([lower_left[0], upper_left[0]]).mean()
    right = np.array([lower_right[0], upper_right[0]]).mean()
    bottom = np.array([lower_left[1], lower_right[1]]).mean()
    top = np.array([upper_left[1], upper_right[1]]).mean()
    print(left, right, bottom, top)
    # this is hack to put the data on a regular grid
    # if the cells do not have even spacing bummer.
    if points:
        east = np.linspace(left, right, num=longitude.size)
        north = np.linspace(bottom, top, num=latitude.size)
    else:
        east = np.linspace(left, right, num=longitude.size + 1)
        north = np.linspace(bottom, top, num=latitude.size + 1)

    east += shift_east
    north += shift_north

    return east, north, utm_zone


def read_nc_file(
    nc_file,
    vtk_fn=None,
    utm_zone=None,
    epsg=None,
    crs=None,
    shift_east=0.0,
    shift_north=0.0,
    units="m",
    shift_z=0.0,
):
    """
    Read NetCDF earth model file into UTM coordinates

    :param nc_file: full path to netCDF file
    :type nc_file: string or Path
    :type longitude: np.ndarray
    :param utm_zone: Desired UTM zone, defaults to None
    :type utm_zone: string, optional
    :param epsg: desired UTM zone, defaults to None
    :type epsg: int, optional
    :param shift_east: meters to shift the grid east, defaults to 0.0
    :type shift_east: float, optional
    :param shift_north: meters to shift the grid north, defaults to 0.0
    :type shift_north: float, optional
    :return: east, north, utm_zone
    :rtype: float, float, string

    """
    nc_file = Path(nc_file)

    if units == "m":
        scale = 1.0
    elif units == "km":
        scale = 1.0 / 1000.0

    if vtk_fn is None:
        vtk_fn = nc_file.parent.joinpath(nc_file.stem)

    # read .nc file into an xarray dataset
    nc_obj = xr.open_dataset(nc_file)

    if nc_obj.depth.units == "km":
        d_scale = 1000
    else:
        d_scale = 1

    # get appropriate grid values
    depth = nc_obj.depth.values * d_scale + shift_z

    # check longitude if its in 0 - 360 mode:
    if nc_obj.longitude.max() > 180:
        nc_obj = nc_obj.assign_coords(
            {"longitude": nc_obj.longitude.values[:] - 360}
        )
    grid_east, grid_north, utm_zone = project_grid(
        nc_obj.latitude.values,
        nc_obj.longitude.values,
        utm_zone=utm_zone,
        epsg=epsg,
        pyproj_str=crs,
        shift_east=shift_east,
        shift_north=shift_north,
    )
    print(f"Projected to {utm_zone}")

    values_dict = {}
    for key, value in nc_obj.variables.items():
        if key in ["depth", "latitude", "longitude"]:
            continue
        v_array = np.zeros(
            (nc_obj.latitude.size, nc_obj.longitude.size, nc_obj.depth.size)
        )
        for z_index in range(depth.size):
            v_array[:, :, z_index] = value[z_index, :, :]
        values_dict[key] = v_array

    # need to add another cell to the depth
    depth = np.append(depth, depth[-1] + (depth[-1] - depth[-2]))
    # print(depth.shape, grid_east.shape, grid_north.shape)
    gridToVTK(
        vtk_fn.as_posix(),
        grid_north * scale,
        grid_east * scale,
        depth * scale,
        values_dict,
    )

    print(f"--> Wrote VTK file to {vtk_fn}")
    return nc_obj, (grid_north * scale, grid_east * scale, depth * scale)


def read_nc_file_points(
    nc_file,
    vtk_fn=None,
    utm_zone=None,
    epsg=None,
    crs=None,
    shift_east=0.0,
    shift_north=0.0,
    units="m",
    shift_z=0.0,
    z_key="depth",
    bbox=None,
):
    """
    Read NetCDF earth model file into UTM coordinates

    :param nc_file: full path to netCDF file
    :type nc_file: string or Path
    :type longitude: np.ndarray
    :param utm_zone: Desired UTM zone, defaults to None
    :type utm_zone: string, optional
    :param epsg: desired UTM zone, defaults to None
    :type epsg: int, optional
    :param shift_east: meters to shift the grid east, defaults to 0.0
    :type shift_east: float, optional
    :param shift_north: meters to shift the grid north, defaults to 0.0
    :type shift_north: float, optional
    :return: east, north, utm_zone
    :rtype: float, float, string

    """
    nc_file = Path(nc_file)

    if units == "m":
        scale = 1.0
    elif units == "km":
        scale = 1.0 / 1000.0

    if vtk_fn is None:
        vtk_fn = nc_file.parent.joinpath(nc_file.stem)

    # read .nc file into an xarray dataset
    nc_obj = xr.open_dataset(nc_file)

    if nc_obj.depth.units == "km":
        d_scale = 1000
    else:
        d_scale = 1

    # check longitude if its in 0 - 360 mode:
    if nc_obj.longitude.max() > 180:
        nc_obj = nc_obj.assign_coords(
            {"longitude": nc_obj.longitude.values[:] - 360}
        )

    grid_east, grid_north, utm_zone = project_grid(
        nc_obj.latitude.values,
        nc_obj.longitude.values,
        utm_zone=utm_zone,
        epsg=epsg,
        pyproj_str=crs,
        shift_east=shift_east,
        shift_north=shift_north,
        points=True,
    )
    print(f"Projected to {utm_zone}")
    xg, yg = np.meshgrid(grid_east, grid_north)
    xg = xg[::-1, ::-1].ravel() * scale
    yg = yg[::-1, ::-1].ravel() * scale

    # get appropriate grid values
    depth = (nc_obj.depth.values.ravel() * d_scale + shift_z) * scale
    depth = depth.astype(xg.dtype)

    values_dict = {}
    for key, value in nc_obj.variables.items():
        if key in ["latitude", "longitude"]:
            continue
        value = value.values.ravel()
        values_dict[key] = value.astype(xg.dtype)

    pointsToVTK(
        vtk_fn.as_posix(),
        yg,
        xg,
        depth,
        values_dict,
    )

    print(f"--> Wrote VTK file to {vtk_fn}")
    return nc_obj, (yg, xg, depth)


# =============================================================================
# test
# =============================================================================
nc_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\earth_models")

points = False
# custom_crs = "+proj=tmerc +lat_0=0 +lon_0=-113.25 +k=0.9996 +x_0=4511000 +y_0=0 +ellps=WGS84 +units=m +no_defs"
custom_crs = None
# northern CA/NV model center
# model_center = (39.635149, -119.803946)
# model_utm = "11S"

# SWUS model
# model_center = (40.75, -113.25)
# model_utm = "11S"

# # Great Basin
# model_center = (38.615252, -119.015192)
# model_utm = "11S"

## Clear Lake
model_center = (38.986014, -122.778463)
model_utm = "10S"

if custom_crs is None:
    model_east, model_north, model_utm = gis_tools.project_point_ll2utm(
        model_center[0], model_center[1], utm_zone=model_utm
    )
else:
    default_proj = proj.Proj(init="epsg:4326")
    custom_proj = proj.Proj(custom_crs)
    model_east, model_north = proj.transform(
        default_proj, custom_proj, model_center[1], model_center[0]
    )

    utm_zone = "custom"

# relative shifts to center model on mt mode
# NWUS11 - CA/NV
# rel_shift_east = -model_east + 250000.
# rel_shift_north = -model_north + 105000.

# CAS19 - CA/NV
# rel_shift_east = -model_east + 150000
# rel_shift_north = -model_north

# wUS-SH-2010 - CA/NV
# rel_shift_east = -model_east + 150000
# rel_shift_north = -model_north - 100000

# moho_temperature - CA/NV
# rel_shift_east = -model_east + 150000
# rel_shift_north = -model_north - 250000

# WUS_2010 -> SWUS
rel_shift_east = -model_east
rel_shift_north = -model_north

nc_list = [
    {"fn": "western_us_NWUS11-vp_vs.nc", "points": False},
    {"fn": "western_us_DNA13_percent.nc", "points": False},
    {"fn": "western_us_s_waves_wUS-SH-2010_percent.nc", "points": False},
    {"fn": "western_us_s_waves_WUS-CAMH-2015.nc", "points": False},
    {"fn": "western_us_s_waves_Casc19-VS.nc", "points": False},
    {"fn": "moho_temperature_great_basin.nc", "points": True},
]

for nc_entry in nc_list[:-1]:

    nc_fn = nc_path.joinpath(nc_entry["fn"])
    save_fn = Path(
        r"c:\Users\jpeacock\OneDrive - DOI\Clearlake\modem_inv",
        nc_fn.stem,
    )

    if nc_entry["points"]:
        x_obj, grid = read_nc_file_points(
            nc_fn,
            vtk_fn=save_fn,
            utm_zone=model_utm,
            crs=custom_crs,
            shift_east=rel_shift_east,
            shift_north=rel_shift_north,
            units="km",
        )
    else:
        x_obj, grid = read_nc_file(
            nc_fn,
            vtk_fn=save_fn,
            utm_zone=model_utm,
            crs=custom_crs,
            shift_east=rel_shift_east,
            shift_north=rel_shift_north,
            units="km",
        )

# vp = np.nan_to_num(nc_obj.variables["vp"][:])
# dvp = nc_obj.variables["dvp_ulberg_mask"][:]


#
# for zz in range(depth.size):
#    raster_fn = os.path.join(r"c:\Users\jpeacock\Documents\iMush\dvp_depth_slices_ulberg",
#                             "{0:02}_dvp_{1:.0f}_WGS84.tif".format(zz, depth[zz]))
#    raster_fn = raster_fn.replace('-', 'm')
#    a2r.array2raster(raster_fn,
#                     (float(lon.min()), float(lat.min())),
#                     1730.0,
#                     1202.0,
#                     (dvp[zz, :, :]))
