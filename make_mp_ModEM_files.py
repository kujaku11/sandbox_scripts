# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 12:55:59 2014

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os
import numpy as np

save_path = r"/home/jpeacock/Documents/ModEM/MountainPass/Inv01_dp"
if not os.path.isdir(save_path):
    os.mkdir(save_path)
    
inv_periods = np.array([.0015625, .002604, .00625, .015625, .0416, .1,
                        .25, .8, 1.6, 4, 16, 32, 64, 128, 512])

station_list = ['mp{0:02}'.format(ii) for ii in range(1, 20)]
station_list.remove('mp06')

edi_path_dp = r"/mnt/hgfs/MTData/MountainPass/EDI_INV_FILES"

edi_list_dp = [os.path.join(edi_path_dp, '{0}.edi'.format(ss))
               for ss in station_list]

#--> make mesh
m_mesh = modem.Model(edi_list_dp)
m_mesh.cell_size_east = 300
m_mesh.cell_size_north = 300
m_mesh.pad_east = 10
m_mesh.pad_north = 10
m_mesh.pad_z = 4
m_mesh.pad_stretch_h = 2.0
m_mesh.n_layers = 35
m_mesh.z_target_depth = 40000
m_mesh.save_path = save_path
m_mesh.make_mesh()
m_mesh.plot_mesh()
m_mesh.station_locations['elev'][:] = 0.0
m_mesh.res_model = np.zeros((m_mesh.grid_north.shape[0],
                             m_mesh.grid_east.shape[0],
                             m_mesh.grid_z.shape[0]))
                             
m_mesh.res_model[:, :, :] = 100.
m_mesh.write_model_file()
m_data = modem.Data(edi_list=edi_list_dp)
m_data.period_list = inv_periods
m_data.station_locations = m_mesh.station_locations.copy()
m_data.error_egbert = 12
m_data.inv_mode = '2'

m_data.save_path = save_path
m_data.write_data_file(fn_basename='mp_data_err12.dat')

m_cov = modem.Covariance()
m_cov.grid_dimensions = m_mesh.res_model.shape
m_cov.smoothing_east = .5
m_cov.smoothing_north = .5
m_cov.smoothing_z = .5
m_cov.save_path = save_path
m_cov.write_covariance_file()

m_fwd = modem.Control_Fwd()
m_fwd.write_control_file(save_path=save_path)

m_inv = modem.Control_Inv()
m_inv.output_fn = 'mp_dp'
m_inv.save_path = save_path
m_inv.write_control_file()


                 
                   
