# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:02:57 2015

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os
import numpy as np

edi_path = r"c:\Users\jpeacock\Documents\MonoBasin\INV_EDI_FILES"
sv_path = r"c:\Users\jpeacock\Documents\MonoBasin\modem_inv\inv_01"

if not os.path.isdir(sv_path):
    os.mkdir(sv_path)

edi_list = [
    os.path.join(edi_path, edi) for edi in os.listdir(edi_path) if edi.endswith(".edi")
]

m_obj = modem.Model()
m_obj.edi_list = edi_list
m_obj.cell_size_east = 500
m_obj.cell_size_north = 500
m_obj.z1_layer = 10
m_obj.z_target_depth = 50000
m_obj.z_bottom = 300000
m_obj.n_layers = 50
m_obj.pad_east = 16
m_obj.pad_north = 16
m_obj.pad_z = 5
m_obj.pad_stretch_h = 1.5
m_obj.pad_stretch_z = 1.5
m_obj.save_path = sv_path
m_obj.make_mesh()
m_obj.plot_mesh()

m_obj.station_locations["elev"][:] = 0.0
m_obj.write_model_file(model_fn_basename="sm_lv_mb.rho")

d_obj = modem.Data(edi_list=edi_list)
d_obj.period_list = np.logspace(np.log10(1.0 / 1024), np.log10(682), 23)
d_obj.station_locations = m_obj.station_locations.copy()
d_obj.error_egbert = 10
d_obj.error_tipper = 0.1
d_obj.get_mt_dict()
d_obj._fill_data_array()

d_obj.write_data_file(save_path=sv_path, fn_basename="lv_mb_err10_tip10.dat")

d_obj.read_data_file(d_obj.data_fn)
tmax = np.where(abs(d_obj.data_array["tip"]) > 1.5)
d_obj.data_array["tip"][tmax] = 0.0 + 0.0j
tmax = np.where(abs(d_obj.data_array["tip"]) > 0.85)
d_obj.data_array["tip_err"][tmax] = abs(d_obj.data_array["tip"][tmax])
# for bad_station in ['mb133', 'mb191', 'mb174', 'mb189', 'mb198', 'mb108',
#                    'mb235', 'mb209', 'mb212', 'mb161', 'mb192', 'mb236']:
#    ss = np.where(d_obj.data_array['station'] == bad_station)
#    d_obj.data_array[ss]['tip'][:] = 0.0+0.0j
d_obj.write_data_file(
    save_path=sv_path,
    fn_basename="lv_mb_err10_tip10.dat",
    compute_error=False,
    fill=False,
)

##==============================================================================
##  Do all the work
##==============================================================================
# data_fn = r"/home/jpeacock/Documents/ModEM/LV/hydro_inv1/lv_hydro_err07_tip10.dat"
# model_fn = r"/home/jpeacock/Documents/ModEM/LV/hydro_inv1/sm_hydro.rho"
#
# m_obj = modem.Model()
# m_obj.read_model_file(model_fn)
#
##modem_center = (337530., 4183900.)
# modem_center = (333730.+700, 4173370.)
# pad = 2
# cell_size = 100.
# res_air = 1e12
# elev_cell = 20

#### 1.) read in the dem and center it onto the resistivity model
# e_east, e_north, elevation = modem.read_dem_ascii(dem_fn, cell_size=500,
#                                        model_center=modem_center,
#                                        rot_90=3)
#
#### 2.) interpolate the elevation model onto the model grid
# m_elev =  modem.interpolate_elevation(e_east, e_north, elevation,
#                               m_obj.grid_east, m_obj.grid_north, pad=3)
#
#### 3.) make a resistivity model that incoorporates topography
# mod_elev, elev_nodes_z =  modem.make_elevation_model(m_elev, m_obj.nodes_z,
#                                              elevation_cell=elev_cell)
#
#### 4.) write new model file
# m_obj.nodes_z = elev_nodes_z
# m_obj.res_model = mod_elev
# m_obj.write_model_file(save_path=sv_path,
#                       model_fn_basename='sm_hydro_topography.rho')
#
##write new data file
# n_dfn =  modem.change_data_elevation(data_fn, m_obj.model_fn)

# write covariance file
cov = modem.Covariance()
cov.grid_dimensions = m_obj.res_model.shape
cov.mask_arr = np.ones_like(m_obj.res_model)
cov.mask_arr[np.where(m_obj.res_model > 1e10)] = 0
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.save_path = sv_path
cov.write_covariance_file()

# m_obj.write_vtk_file()
# d_obj.write_vtk_station_file()
