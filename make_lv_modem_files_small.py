# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:02:57 2015

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os
import numpy as np

edi_path = r"/mnt/hgfs/Google Drive/Mono_Basin/INV_EDI_FILES"
dem_fn = r"/mnt/hgfs/Google Drive/Mono_Basin/dem_modem.asc"
sv_path = r"/home/jpeacock/Documents/ModEM/LV/hydro_inv1"

if not os.path.isdir(sv_path):
    os.mkdir(sv_path)

station_list = ['mb{0:03}'.format(ii) for ii in [178, 177, 220, 176, 222, 221, 
                175, 224, 225, 188, 235, 236, 237, 190, 226, 179, 180, 181, 
                231, 189, 237, 232, 191, 192, 182, 197, 198, 196, 199, 200, 
                203]]
pw_station_list = ['lv{0:02}'.format(ii) for ii in [22, 21, 20, 14, 15, 16, 
                   17, 18, 19, 11, 4, 12, 3, 2, 13, 10, 9, 6, 7, 8, 24]] 
                   
edi_list = [os.path.join(edi_path, '{0}.edi'.format(ss)) for ss in 
            station_list+pw_station_list]
            
m_obj = modem.Model()
m_obj.edi_list = edi_list
m_obj.cell_size_east = 250
m_obj.cell_size_north = 250
m_obj.z1_layer = 20
m_obj.z_target_depth = 15000
m_obj.z_bottom = 200000
m_obj.n_layers = 30
m_obj.pad_east = 9
m_obj.pad_north = 9
m_obj.pad_stretch_h = 2.1
m_obj.pad_stretch_z = 1.5
m_obj.make_mesh()
m_obj.plot_mesh()
m_obj.save_path = sv_path
m_obj.write_model_file(model_fn_basename='sm_hydro.rho')

d_obj = modem.Data(edi_list=edi_list)
d_obj.period_list = np.logspace(-3, 1, 24)
d_obj.station_locations = m_obj.station_locations.copy()
d_obj.error_egbert = 7
d_obj.error_tipper = 1
d_obj.write_data_file(save_path=sv_path, fn_basename='lv_hydro_err07_tip10.dat')

#==============================================================================
#  Do all the work
#==============================================================================
data_fn = r"/home/jpeacock/Documents/ModEM/LV/hydro_inv1/lv_hydro_err07_tip10.dat"
model_fn = r"/home/jpeacock/Documents/ModEM/LV/hydro_inv1/sm_hydro.rho"

m_obj = modem.Model()
m_obj.read_model_file(model_fn)

#modem_center = (337530., 4183900.)
modem_center = (333730.+700, 4173370.)
pad = 2
cell_size = 100.
res_air = 1e12
elev_cell = 20

### 1.) read in the dem and center it onto the resistivity model 
e_east, e_north, elevation = modem.read_dem_ascii(dem_fn, cell_size=500, 
                                        model_center=modem_center, 
                                        rot_90=3)

### 2.) interpolate the elevation model onto the model grid
m_elev =  modem.interpolate_elevation(e_east, e_north, elevation, 
                               m_obj.grid_east, m_obj.grid_north, pad=3)

### 3.) make a resistivity model that incoorporates topography
mod_elev, elev_nodes_z =  modem.make_elevation_model(m_elev, m_obj.nodes_z, 
                                              elevation_cell=elev_cell) 

### 4.) write new model file  
m_obj.nodes_z = elev_nodes_z
m_obj.res_model = mod_elev
m_obj.write_model_file(save_path=sv_path,
                       model_fn_basename='sm_hydro_topography.rho')

#write new data file                       
n_dfn =  modem.change_data_elevation(data_fn, m_obj.model_fn)

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

m_obj.write_vtk_file()
d_obj.write_vtk_station_file()
