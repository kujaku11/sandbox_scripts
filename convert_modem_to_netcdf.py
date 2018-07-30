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
model_fn = r"c:\Users\jpeacock\Documents\imush\Z4T3_cov0p2x2_L1E2_NLCG_061.rho"
save_fn = r"c:\Users\jpeacock\Documents\imush\bedrosian_imush_mt_2018_log10_clip_iris.nc"
model_center = (-122.080378, 46.387827, )
clip = 14
iris_submit = True
# =============================================================================
# Read in model file
# =============================================================================
m_obj = modem.Model()
m_obj.read_model_file(model_fn)

### --> need to convert model coordinates into lat and lon
utm_center = gis_tools.project_point_ll2utm(model_center[1], model_center[0])
 
lat = np.zeros_like(m_obj.grid_north[clip:-(clip+1)])
lon = np.zeros_like(m_obj.grid_east[clip:-(clip+1)])
depth = m_obj.grid_z[:-1]/1000.

for ii, north in enumerate(m_obj.grid_north[clip:-(clip+1)]):
    m_lat, m_lon = gis_tools.project_point_utm2ll(utm_center[0], 
                                                  utm_center[1]+north,
                                                  utm_center[2])
    lat[ii] = m_lat
    
for ii, east in enumerate(m_obj.grid_east[clip:-(clip+1)]):
    m_lat, m_lon = gis_tools.project_point_utm2ll(utm_center[0]+east, 
                                                  utm_center[1],
                                                  utm_center[2])
    lon[ii] = m_lon
# =============================================================================
# Create NetCDF4 dataset compliant with IRIS format
# =============================================================================
dataset = netcdf.Dataset(save_fn, 'w', format='NETCDF4')
dataset.title = "Electrical Resistivity Model"
dataset.id = "iMUSH_MT_2018"
dataset.summary = "Crustal resistivity model of Mount St. Helens and surrounding \n"+\
                  "area estimated from magnetotelluric data part of the iMUSH project. \n"+\
                  "For more information see Bedrosian et al. (2018)\n"+\
                  "Lat and Lon are from the lower left of each model cell.\n"
dataset.keywords = "electrical resistivity, magnetotellurics, MT, iMUSH, Mount St. Helens, Mount Adams, Mount Rainier, Spirit Lake Pluton" 
dataset.Metadata_Conventions = "Unidata Dataset Discovery v1.0"
dataset.Conventions = "CF-1.0"

#### --> set the metadata
# creator information
dataset.creator_name = "Paul A. Bedrosian"
dataset.creator_url = r"https://crustal.usgs.gov/"
dataset.creator_email = "pbedrosian@usgs.gov"
dataset.institution = "U.S. Geological Survey"
dataset.acknowledgment = "This work was supported by the USGS Volcano Hazards and Mineral Resources Programs and by NSF grant EAR1144353"
dataset.references = "Bedrosian, P. A, Peacock, J. R., Bowles-Martinez, E., Schultz, A., Hill, G. J. \n"+\
                     "(2018), Crustal inheritance and top-down control on arc magmatism a focus on Mount St. Helens, \n"+\
                     "Nature Geoscience, In Press\n"
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
dataset.geospatial_lon_resolution = .01
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
attr_depth.long_name = "Depth below Earth surface"
attr_depth[:] = depth

# resistivity
res = np.log10(m_obj.res_model[clip:-clip, clip:-clip, :])
if iris_submit:
    attr_res = dataset.createVariable("resistivity", "f8", 
                                  ("depth", "latitude", "longitude"))
    
    attr_res[:] = np.swapaxes(np.swapaxes(res, 0, 2), 1, 2)
else:
    attr_res = dataset.createVariable("resistivity", "f8", 
                                      ("longitude", "latitude", "depth"))
    attr_res[:] = np.swapaxes(res, 0, 1)
attr_res.long_name = "Electrical resistivity in Ohm-m"
attr_res.units = "Log10(Ohm-m)"
attr_res.valid_range = (-3, 6)
attr_res.missing_value = 99999.
attr_res.fill_value = 99999.

dataset.close()