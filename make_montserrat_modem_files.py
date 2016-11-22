# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 10:31:45 2016

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os

model_fn = r"/mnt/hgfs/jpeacock/Documents/Montserrat/MONT_Model_100_3.ws"
data_fn = r"/mnt/hgfs/jpeacock/Documents/Montserrat/ModEM_Data_edit_20160125.dat"

#d_obj = modem.Data()
#d_obj.read_data_file(data_fn)
#
## make elevation of station location 0.0, no topography
#for key in d_obj.mt_dict.keys():
#    mt_obj = d_obj.mt_dict[key]
#    mt_obj.elev = 0.0
#    d_obj.mt_dict[key] = mt_obj
#    
#d_obj.write_data_file(fn_basename=r"Mont_no_elevation.dat", compute_error=False)
ws_init = modem.ws.WSMesh()
ws_init.read_initial_file(model_fn)
ws_init.res_model[:, :, :] = 100.00
   
m_obj = modem.Model()
m_obj.grid_center = (-294750.0-625.0, -296000.0+450.0, 0)
m_obj.write_model_file(nodes_east=ws_init.nodes_east, 
                       nodes_north=ws_init.nodes_north,
                       nodes_z=ws_init.nodes_z,
                       model_fn_basename=r"Mont_ModEM_sm02.rho",
                       save_path=os.path.dirname(model_fn),
                       res_model=ws_init.res_model)

cov = modem.Covariance(grid_dimensions=m_obj.res_model.shape)
cov.smoothing_east = .4
cov.smoothing_north = .4
cov.smoothing_z = .4
cov.save_path = m_obj.save_path
cov.write_covariance_file()