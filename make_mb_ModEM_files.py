# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 12:55:59 2014

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os
import numpy as np

save_path = r"/home/jpeacock/Documents/ModEM/MB_MT/Inv2_dp"
if not os.path.isdir(save_path):
    os.mkdir(save_path)
    
inv_periods = [.05, .5, 2, 8, 16, 64, 256]

station_list = [17, 18, 25, 26, 34, 36, 40, 41, 46, 49, 51, 54, 55, 57, 59,
                60, 63, 64, 65, 67, 68, 69, 70, 71, 72, 73, 74, 75, 89, 90, 91,
                92, 93, 108,  110, 112, 113, 115, 118, 119, 124,
                125, 126, 129, 130, 141, 142, 143, 150, 151, 153, 154, 156,
                157, 158, 159, 161, 133]


edi_path_dp = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files_dp"
#edi_path_ga = r"/mnt/hgfs/Google Drive/Mono_Basin/EDI_Files_ga"

#edi_list_lv = [os.path.join(edi_path_lv, 'LV{0:02}.edi'.format(ss))
#               for ss in lv_list]

#edi_list_ps = [os.path.join(edi_path_ps, 'mb{0:03}_ps.edi'.format(ss))
#               for ss in station_list]
edi_list_dp = [os.path.join(edi_path_dp, 'mb{0:03}_dp.edi'.format(ss))
               for ss in station_list]
#edi_list_ga = [os.path.join(edi_path_ga, 'mb{0:03}_ga.edi'.format(ss))
#               for ss in station_list]

#--> make mesh
m_mesh = modem.Model(edi_list_dp)
m_mesh.pad_east = 9
m_mesh.pad_north = 9
m_mesh.pad_z = 4
m_mesh.pad_stretch_h = 1.8
m_mesh.n_layers = 40
m_mesh.z_target_depth = 30000
m_mesh.save_path = save_path
m_mesh.make_mesh()
m_mesh.plot_mesh()
m_mesh.res_model = np.zeros((m_mesh.grid_north.shape[0],
                             m_mesh.grid_east.shape[0],
                             m_mesh.grid_z.shape[0]))
                             
m_mesh.res_model[:, :, :] = 1000.
m_mesh.write_model_file()

m_data = modem.Data(edi_list=edi_list_dp)
m_data.period_list = inv_periods
m_data.station_locations = m_mesh.station_locations.copy()
m_data.error_egbert = 7
m_data.error_tipper = .5
m_data.save_path = save_path
m_data.write_data_file()

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
m_inv.output_fn = 'mb_dp'
m_inv.save_path = save_path
m_inv.write_control_file()


                 
                   
