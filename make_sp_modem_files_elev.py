# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:02:57 2015

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os
import numpy as np

edi_path = r"d:\Peacock\MTData\SanPabloBay\EDI_Files_dp"
dem_fn = r"c:\Users\jpeacock\Documents\SanPabloBay\sp_10mtopo_bathy.asc"
sv_path = r"c:\Users\jpeacock\Documents\SanPabloBay\Inv01_dp_elev"
#edi_path = r"/mnt/hgfs/MTData/SanPabloBay/EDI_Files_dp"
#dem_fn = r"/mnt/hgfs/jpeacock/Documents/SanPabloBay/sp_10mtopo_bathy.asc"
#sv_path = r"/home/jpeacock/Documents/ModEM/SanPabloBay/Inv01_dp_elev"

if not os.path.isdir(sv_path):
    os.mkdir(sv_path)
                   
edi_list = [os.path.join(edi_path, ss) for ss in 
            os.listdir(edi_path) if ss.find('.edi') > 0]
            
m_obj = modem.Model()
m_obj.edi_list = edi_list
m_obj.cell_size_east = 100
m_obj.cell_size_north = 100
m_obj.z1_layer = 2
m_obj.z_target_depth = 20000
m_obj.z_bottom = 200000
m_obj.n_layers = 40
m_obj.pad_east = 15
m_obj.pad_north = 15
m_obj.pad_z = 5
m_obj.pad_stretch_h = 1.8
m_obj.pad_stretch_z = 1.5
m_obj.make_mesh()
m_obj.plot_mesh()
m_obj.save_path = sv_path
m_obj.station_locations['elev'][:] = 0.0
m_obj.write_model_file(model_fn_basename='sp_sm_topo.rho')

d_obj = modem.Data(edi_list=edi_list)
d_obj.period_list = np.logspace(-3, 2.5, 17)
d_obj.station_locations = m_obj.station_locations.copy()

d_obj.error_egbert = 7
d_obj.error_tipper = .05
d_obj.write_data_file(save_path=sv_path, fn_basename='sp_data_err10_tip05.dat')

##==============================================================================
##  Do all the work
##==============================================================================

#data_fn = r"c:\Users\jpeacock\Documents\SanPabloBay\Inv01_dp_elev\sp_data_err10_tip05.dat"
#model_fn = r"c:\Users\jpeacock\Documents\SanPabloBay\Inv01_dp_elev\sp_sm_topo.rho"

#m_obj = modem.Model()
#m_obj.read_model_file(m_obj.model_fn)
#
#d_obj = modem.Data()
#d_obj.read_data_file(data_fn)

#modem_center = (337530., 4183900.)
modem_center = (544750., 4220700.)
pad = 3
cell_size = 50.
res_air = 1e12
elev_cell = 2

### 1.) read in the dem and center it onto the resistivity model 
e_east, e_north, elevation = modem.read_dem_ascii(dem_fn, cell_size=50, 
                                        model_center=modem_center, 
                                        rot_90=0)

### 2.) interpolate the elevation model onto the model grid
m_elev =  modem.interpolate_elevation(e_east, e_north, elevation, 
                               m_obj.grid_east, m_obj.grid_north, pad=1)

m_elev[np.where(m_elev > 10)] = 10.0
### 3.) make a resistivity model that incoorporates topography
mod_elev, elev_nodes_z =  modem.make_elevation_model(m_elev, m_obj.nodes_z, 
                                              elevation_cell=elev_cell) 

### 4.) write new model file  
m_obj.nodes_z = elev_nodes_z
m_obj.res_model = mod_elev
m_obj.write_model_file(save_path=sv_path,
                       model_fn_basename='sm_hydro_topography.rho')

#write new data file                       
n_dfn = modem.change_data_elevation(d_obj.data_fn, m_obj.model_fn)

# write covariance file
cov = modem.Covariance()
#cov.grid_dimensions = m_obj.res_model.shape
#cov.mask_arr = np.ones_like(m_obj.res_model)
#cov.mask_arr[np.where(m_obj.res_model > 1e10)] = 0
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4
cov.save_path = sv_path
cov.write_covariance_file(model_fn=m_obj.model_fn)

#m_obj.write_vtk_file()
#d_obj.write_vtk_station_file()
