# -*- coding: utf-8 -*-
"""
Convert modem model to netcdf format for archiving at Iris

Created on Mon Jul 09 12:31:01 2018

@author: jpeacock
"""
import numpy as np
import netCDF4 as netcdf
import mtpy.modeling.modem as modem
import mtpy.utils.gis_tools as gis_tools

# =============================================================================
# Inputs
# =============================================================================
model_fn = r"c:\Users\jpeacock\Documents\Geothermal\GraniteSprings\modem_inv\inv_02_tip\gs_prm_err03_tip02_cov03_NLCG_129.rho"
save_fn = r"c:\Users\jpeacock\Documents\Geothermal\GraniteSprings\modem_inv\inv_02_tip\granite_springs_pfa_mt_2018_usgs.nc"
cfg_fn = r"C:\Users\jpeacock\Documents\mt_model_netcdf_granite_springs.cfg"
model_center = (
    -118.927443,
    40.227213,
)
clip = 8
iris_submit = True
# =============================================================================
# Read in model file
# =============================================================================
def clip_modem_model(model_fn, clip):
    """
    Read in ModEM model and clip to a smaller box
    """
    m_obj = modem.Model()
    m_obj.read_model_file(model_fn)

    ### --> need to convert model coordinates into lat and lon
    utm_center = gis_tools.project_point_ll2utm(model_center[1], model_center[0])

    lat = np.zeros_like(m_obj.grid_north[clip : -(clip + 1)])
    lon = np.zeros_like(m_obj.grid_east[clip : -(clip + 1)])
    depth = m_obj.grid_z[:-1] / 1000.0

    for ii, north in enumerate(m_obj.grid_north[clip : -(clip + 1)]):
        m_lat, m_lon = gis_tools.project_point_utm2ll(
            utm_center[0], utm_center[1] + north, utm_center[2]
        )
        lat[ii] = m_lat

    for ii, east in enumerate(m_obj.grid_east[clip : -(clip + 1)]):
        m_lat, m_lon = gis_tools.project_point_utm2ll(
            utm_center[0] + east, utm_center[1], utm_center[2]
        )
        lon[ii] = m_lon

    res = np.log10(m_obj.res_model[clip:-clip, clip:-clip, :])

    return lat, lon, depth, res


# =============================================================================
# Create NetCDF4 dataset compliant with IRIS format
# =============================================================================
def read_cfg(netcdf_cfg):
    """
    read in configuration file for netcdf file
    """
    with open(netcdf_cfg, "r") as fid:
        lines = fid.readlines()

    return_dict = {}
    for line in lines:
        key, value = [k_str.strip() for k_str in line.strip().split("=")]
        return_dict[key] = value

    return return_dict


def write_netcdf(
    netcdf_fn, model_fn, clip, model_center, netcdf_cfg_fn=None, iris_submit=True
):
    """
    write netcdf file

    netcdf config file
    """
    ### Clip model
    lat, lon, depth, res = clip_modem_model(model_fn, clip)

    ### make netcdf object
    dataset = netcdf.Dataset(save_fn, "w", format="NETCDF4")

    ### read in configuration file
    if netcdf_cfg_fn is not None:
        cfg_dict = read_cfg(netcdf_cfg_fn)
        for key, value in cfg_dict.items():
            setattr(dataset, key, value)

    dataset.Metadata_Conventions = "Unidata Dataset Discovery v1.0"
    dataset.Conventions = "CF-1.0"

    #### --> set the metadata
    ### -> metadata lat
    dataset.geospatial_lat_min = "{0:.2f}".format(lat.min())
    dataset.geospatial_lat_max = "{0:.2f}".format(lat.max())
    dataset.geospatial_lat_units = "degrees_north"
    dataset.geospatial_lat_resolution = 0.01
    ### -> metadata lon
    dataset.geospatial_lon_min = "{0:.2f}".format(lon.min())
    dataset.geospatial_lon_max = "{0:.2f}".format(lon.max())
    dataset.geospatial_lon_units = "degrees_north"
    dataset.geospatial_lon_resolution = 0.01
    dataset.geospatial_vertical_min = "{0:.2f}".format(depth.min())
    dataset.geospatial_vertical_max = "{0:.2f}".format(depth.max())
    ### -> metadata depth
    dataset.geospatial_vertical_units = "kilometer"
    dataset.geospatial_vertical_resolution = 0.0001
    dataset.geospatial_vertical_positive = "Down"
    dataset.time_coverage_start = "2014"
    dataset.time_coverage_end = "2016"

    ### --> set dimensions
    dim_lat = dataset.createDimension("latitude", lat.size)
    dim_lon = dataset.createDimension("longitude", lon.size)
    dim_depth = dataset.createDimension("depth", depth.size)

    ### --> set attributes
    # latitude
    attr_lat = dataset.createVariable("latitude", "f8", ("latitude",))
    attr_lat.units = "degrees_north"
    attr_lat.long_name = "Latitude; positive north"
    attr_lat.standard_name = "latitude"
    attr_lat[:] = lat

    # longitude
    attr_lon = dataset.createVariable("longitude", "f8", ("longitude",))
    attr_lon.units = "degrees_east"
    attr_lon.long_name = "Longitude; positive east"
    attr_lon.standard_name = "longitude"
    attr_lon[:] = lon

    # depth
    attr_depth = dataset.createVariable("depth", "f8", ("depth",))
    attr_depth.units = "kilometer"
    attr_depth.positive = "down"
    attr_depth.long_name = "Depth below Earth surface"
    attr_depth[:] = depth

    # resistivity

    if iris_submit:
        attr_res = dataset.createVariable(
            "resistivity", "f8", ("depth", "latitude", "longitude")
        )

        attr_res[:] = np.swapaxes(np.swapaxes(res, 0, 2), 1, 2)
    else:
        attr_res = dataset.createVariable(
            "resistivity", "f8", ("longitude", "latitude", "depth")
        )
        attr_res[:] = np.swapaxes(res, 0, 1)
    attr_res.long_name = "Electrical resistivity in Ohm-m"
    attr_res.units = "Log10(Ohm-m)"
    attr_res.valid_range = (-3, 6)
    attr_res.missing_value = 99999.0
    attr_res.fill_value = 99999.0

    dataset.close()

    return netcdf_fn


# =============================================================================
# Run
# =============================================================================
write_netcdf(save_fn, model_fn, clip, model_center, cfg_fn)
