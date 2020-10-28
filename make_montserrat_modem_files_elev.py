# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:02:57 2015

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import os
import numpy as np

reload(modem)
# ==============================================================================
# Input files
# ==============================================================================
dem_fn = r"c:\Users\jpeacock\Documents\Montserrat\Mont_bath\mont_bathym_dem.asc"
bathym_fn = (
    r"c:\Users\jpeacock\Documents\Montserrat\Caribbean_DEM\gebco_2014_30s_ascii.txt"
)

data_fn = r"c:\Users\jpeacock\Documents\Montserrat\modem_inv\Inv04_dr\mont_modem_data_err10_tip05.dat"
model_fn = r"c:\Users\jpeacock\Documents\Montserrat\modem_inv\Inv04_dr\mont_base.rho"

# path to save files to
sv_path = r"c:\Users\jpeacock\Documents\Montserrat\modem_inv\Inv05_dr"

if not os.path.exists(sv_path):
    os.mkdir(sv_path)
# ==============================================================================
# Input Parameters
# ==============================================================================
# center is (easting, northing)
# mont_model_center = (585010., 1851000.)
# mont_model_center = (584010., 1851330.)
# mont_model_center = (583337., 1849383.+1400.)

pad = 5
dem_cell_size = 200.0
bathym_cell_size = 900
res_air = 1e12
elev_cell = 30

# starting model resistivity
sm_res = 100

##==============================================================================
##  Do all the work
##==============================================================================

m_obj = modem.Model()
m_obj.read_model_file(model_fn)

d_obj = modem.Data()
d_obj.read_data_file(data_fn)
mont_model_center = (d_obj.center_point.east + 1200, d_obj.center_point.north + 2900)

m_obj.add_topography_to_model(
    dem_fn, model_center=mont_model_center, cell_size=dem_cell_size, elev_cell=30
)

#### 1.) read in the dem and center it onto the resistivity model
# e_east, e_north, elevation = modem.read_dem_ascii(dem_fn, cell_size=dem_cell_size,
#                                        model_center=mont_model_center,
#                                        rot_90=0)
#
#### 1b) need to remove the non data points and set them to the minimum value
#### because they are usually at the edges of the grid.
# elevation[np.where(elevation == -9999.0)] = elevation[np.where(elevation != -9999.0)].min()
#
##### 1c) read in bathymetry data
##b_east, b_north, bathymetry = modem.read_dem_ascii(bathym_fn,
##                                                   cell_size=bathym_cell_size,
##                                                   model_center=mont_model_center,
##                                                   rot_90=0)
#
#### 2a) interpolate the elevation model onto the model grid
# m_elev =  modem.interpolate_elevation(e_east,
#                                      e_north,
#                                      elevation,
#                                      m_obj.grid_east,
#                                      m_obj.grid_north,
#                                      pad=1)
#
#### 2b)
#
#### 2c) need to merge the two together  can't interpolate bathymetry, its too
#### large, need to think of a more clever way to add in long distance
#### bathymetry.  Maybe interpolate onto the coarser grid of the padding cells
#### then add it to m_elev?
#
#### 3.) make a resistivity model that incoorporates topography
# res_mod_elev, elev_nodes_z =  modem.make_elevation_model(m_elev, m_obj.nodes_z,
#                                                         elevation_cell=elev_cell,
#                                                         fill_res=sm_res)
# there is data missing in the res mod so it puts sea water down to
# unreasonable depths, set those cells to starting model resistivity
m_obj.res_model[:, :, 43:][np.where(m_obj.res_model[:, :, 43:] == 0.3)] = sm_res

### 4.) write new model file
m_obj.model_fn = None
m_obj.write_model_file(
    **{"save_path": sv_path, "model_fn_basename": "mont_topography.rho"}
)

# write new data file
d_obj.center_stations(m_obj.model_fn)
d_obj.change_data_elevation(m_obj.model_fn)

n_dfn = d_obj.write_data_file(
    fn_basename=r"mont_data_topo_c.dat", compute_error=False, fill=False, elevation=True
)

# write covariance file
cov = modem.Covariance()
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.save_path = sv_path
cov.write_covariance_file(model_fn=m_obj.model_fn)

# m_obj.write_vtk_file()
# d_obj.write_vtk_station_file()

mm = modem.ModelManipulator(
    model_fn=m_obj.model_fn,
    data_fn=n_dfn,
    depth_index=26,
    xlimits=(-10, 10),
    ylimits=(-10, 10),
)
