# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:02:57 2015

Add topography to ModEM models and data file, and covariance

@author: jpeacock
"""
# ==============================================================================
# Imports
# ==============================================================================
import os
import mtpy.modeling.modem as modem

# ==============================================================================
# Input files
# ==============================================================================
dem_fn = r"c:\Users\jpeacock\Documents\ClearLake\dem\geysers_dem.txt"

data_fn = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv02_dr\geysers_modem_data_err07.dat"
model_fn = (
    r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv02_dr\geysers_modem_sm_02.rho"
)

# path to save files to
sv_path = r"c:\Users\jpeacock\Documents\ClearLake\modem_inv\inv03_dr"

if not os.path.exists(sv_path):
    os.mkdir(sv_path)
# ==============================================================================
# Input Parameters
# ==============================================================================
# number of cells to make elevation similar from edge of model
pad = 5

# cell size of dem
dem_cell_size = 200.0

# air resistivity
res_air = 1e12

# size of elevation cells
elev_cell = 30

##==============================================================================
##  Do all the work
##==============================================================================
m_obj = modem.Model()
m_obj.read_model_file(model_fn)

d_obj = modem.Data()
d_obj.read_data_file(data_fn)

# sometimes you need to adjust the center of the model, distance is in meters
model_center = (d_obj.center_point.east - 500, d_obj.center_point.north + 200)

# add topography to model, can set a max elevation to remove isolated peaks
# which can cause errors in ModEM
new_model_fn = m_obj.add_topography_to_model(
    dem_fn,
    model_fn,
    model_center=model_center,
    cell_size=dem_cell_size,
    elev_cell=elev_cell,
    elev_max=1260.0,
)


# write new data file
n_dfn = d_obj.change_data_elevation(
    d_obj.data_fn, new_model_fn, new_data_fn=os.path.join(sv_path, "gz_data_topo.dat")
)

# write covariance file
cov = modem.Covariance()
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.save_path = sv_path
cov.write_covariance_file(model_fn=new_model_fn)

# make paraview files if needed
m_obj.write_vtk_file()
d_obj.write_vtk_station_file()

# plot the model and make sure everything looks good
mm = modem.ModelManipulator(
    model_fn=new_model_fn,
    data_fn=n_dfn,
    depth_index=42,
    xlimits=(-200, 10),
    ylimits=(-200, 200),
)
