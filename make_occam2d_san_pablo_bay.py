# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 13:51:54 2015

@author: jpeacock
"""

import mtpy.modeling.occam2d_rewrite as occam
import numpy as np

s_edi_path = r"d:\Peacock\MTData\SanPabloBay\EDI_Files_dp"
s_list = ['sp{0:02}'.format(ii) for ii in range(1, 16)] 

ocd = occam.Data(edi_path=s_edi_path, station_list=s_list)
ocd.geoelectric_strike = 0.0
ocd.model_mode = 'log_tm_tip'
ocd.phase_tm_err = 2.5
ocd.res_tm_err = 20
ocd.tipper_err = 10
ocd.res_te_err = 20
ocd.phase_te_err = 2.5
ocd.save_path = r"c:\MinGW32-xy\Peacock\occam\SanPabloBay\inv02_tm_tip"
ocd._rotate_to_strike = False
ocd.write_data_file()

ocm = occam.Regularization(station_locations=ocd.station_locations)
ocm.cell_width = 50
ocm.n_layers = 110
ocm.z1_layer = 2
ocm.z_target_depth = 20000
ocm.x_pad_multiplier = 1.5
ocm.num_x_pad_cells = 9
ocm.num_x_pad_small_cells = 5
ocm.build_mesh()
ocm.save_path = ocd.save_path
ocm.write_mesh_file()
ocm.build_regularization()
ocm.write_regularization_file()
ocm.plot_mesh()

ocs = occam.Startup()
ocs.data_fn = ocd.data_fn
ocs.resistivity_start = 1
ocs.model_fn = ocm.reg_fn
ocs.param_count = ocm.num_free_param
ocs.save_path = ocd.save_path
ocs.write_startup_file()

#mask large tipper values in data file
data_fn = ocd.data_fn
ocd = occam.Data()
ocd.read_data_file(data_fn)

for s_dict in ocd.data:
    re_index = np.where(abs(s_dict['re_tip'][0]) > 1.0)
    im_index = np.where(abs(s_dict['im_tip'][0]) > 1.0)
    s_dict['re_tip'][0][re_index] = 0.0
    s_dict['im_tip'][0][re_index] = 0.0
    s_dict['re_tip'][0][im_index] = 0.0
    s_dict['im_tip'][0][im_index] = 0.0

# give station 6 larger error bars
ocd.data[5]['tm_phase'][1] *= 20
ocd.data[5]['tm_res'][1] *= 10

ocd.model_mode = 'log_tm_tip'
ocd.write_data_file(data_fn='{0}_masked.dat'.format(data_fn[:-4]))

