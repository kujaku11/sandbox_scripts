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
model_fn = r"c:\Users\jpeacock\Documents\TorC\tc_z03_t02_c02_NLCG_041.rho"
model_center = (-107.347830, 33.228427)
# =============================================================================
# Read in model file
# =============================================================================
m_obj = modem.Model()
m_obj.read_model_file(model_fn)

### --> need to convert model coordinates into lat and lon
utm_center = gis_tools.project_point_ll2utm(model_center[1], model_center[0])
 
lat = np.zeros_like(m_obj.grid_north[:-1])
lon = np.zeros_like(m_obj.grid_east[:-1])
depth = m_obj.grid_z[:-1]


for ii, north in enumerate(m_obj.grid_north[:-1]):
    m_lon, m_lat = gis_tools.project_point_utm2ll(utm_center[0], 
                                                  utm_center[1]+north/2.,
                                                  utm_center[2])
    lat[ii] = m_lat
    
for ii, east in enumerate(m_obj.grid_east[:-1]):
    m_lon, m_lat = gis_tools.project_point_utm2ll(utm_center[0]+east/2., 
                                                  utm_center[1],
                                                  utm_center[2])
    lon[ii] = m_lon
# =============================================================================
# Create NetCDF4 dataset compliant with IRIS format
# =============================================================================
dataset = netcdf.Dataset(r"c:\Users\jpeacock\Documents\test.nc", 'w',
                         format='NETCDF4')
dataset.title = "Electrical Resistivity Model"
dataset.id = "Model ID"
dataset.summary = "Electrical resistivity developed from magnetotelluric data "+\
                  "part of the iMUSH project. \n"+\
                  "For more information see Bedrosian et al. (2018)\n"+\
                  "Lat and Lon are from the south western corner of each model cell.\n"
dataset.keywords = "electrical resistivity, magnetotellurics, iMUSH" 
dataset.Metadata_Conventions = "Unidata Dataset Discovery v1.0"
dataset.Conventions = "CF-1.0"

#### --> set the metadata
# creator information
dataset.creator_name = "Paul Bedrosian"
dataset.creator_url = r"https://crustal.usgs.gov/"
dataset.creator_email = "pbedrosian@usgs.gov"
dataset.institution = "U.S. Geological Survey"
dataset.acknowledgment = "Supported by NSF EAR1144353"
dataset.references = "Bedrosian, P. A, Peacock, J. R., Bowles-Martinez, E., Schultz, A., Hill, G. J. \n"+\
                     "(2018), Crustal inheritance and top-down control on arc magmatism a focus on Mount St. Helens, \n"+\
                     "Nature Geoscience, In Print\n"
dataset.history = "U.S. Geological Survey Model 2018"
dataset.comment  = "Model converted to netCDF by IRIS DMC"
### -> metadata lat
dataset.geospatial_lat_min = '{0:.2f}'.format(lat.min())
dataset.geospatial_lat_max = '{0:.2f}'.format(lat.max())
dataset.geospatial_lat_units = "degrees_north"
dataset.geospatial_lat_resolution = .01
### -> metadata lon
dataset.geospatial_lon_min = '{0:.2f}'.format(lon.min())
dataset.geospatial_lon_max = '{0:.2f}'.format(lon.max())
dataset.geospatial_lon_units = "degrees_north"
dataset.geospatial_lon_resolution = ".01"
dataset.geospatial_vertical_min = '{0:.2f}'.format(depth.min())
dataset.geospatial_vertical_max = '{0:.2f}'.format(depth.max())
### -> metadata depth
dataset.geospatial_vertical_units = "kilometer"
dataset.geospatial_vertical_resolution = .0001
dataset.geospatial_vertical_positive = "Down"
dataset.time_coverage_start = "2014"
dataset.time_coverage_end = "2016"

### --> set dimensions
dim_lat = dataset.createDimension("latitude", lat.size)
dim_lon = dataset.createDimension("longitude", lon.size)
dim_depth = dataset.createDimension("depth", m_obj.grid_z.size-1)

### --> set attributes
# latitude
attr_lat = dataset.createVariable("latitude", "f8", ("latitude", ))
attr_lat.units = "degrees_north"
attr_lat.long_name = "Latitude; positive north"
attr_lat.standard_name = 'latitude'
attr_lat[:] = lat

# longitude
attr_lon = dataset.createVariable("longitude", "f8", ("longitude", ))
attr_lon.units = "degrees_east"
attr_lon.long_name = "Longitude; positive east"
attr_lon.standard_name = 'longitude'
attr_lon[:] = lon

# depth
attr_depth = dataset.createVariable("depth", "f8", ("depth", ))
attr_depth.units = "kilometer"
attr_depth.positive = "down"
attr_depth.long_name = "depth below Earth surface"
attr_depth[:] = depth

# resistivity
attr_res = dataset.createVariable("resistivity", "f8", 
                                  ("latitude", "longitude", "depth"))
attr_res.long_name = "Electrical resistivity in Ohm-m"
attr_res.units = "Ohm-m"
attr_res.valid_range = (.01, 10000.)
#attr_res.valid_range_min = "0.01"
#attr_res.valid_range_max = "10000."
attr_res.missing_value = 99999.
attr_res.FillValue = 99999.
attr_res[:] = m_obj.res_model

dataset.close()