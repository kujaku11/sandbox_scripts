# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 13:51:54 2015

@author: jpeacock
"""

import mtpy.modeling.occam2d_rewrite as occam

s_edi_path = r"c:\Users\jpeacock\Documents\Geothermal\TorC\EDI_Files_INV"
s_list = ['TC{0:03}'.format(ii) for ii in range(3, 13)] 

ocd = occam.Data(edi_path=s_edi_path, station_list=s_list)
ocd.model_mode = 'log_all'
ocd.phase_tm_err = 5
ocd.res_tm_err = 30
ocd.phase_te_err = 5
ocd.res_te_err = 30
ocd.tipper_err = 5
ocd.save_path = r"c:\MinGW32-xy\Peacock\occam\Folsom\inv02_torc_all"
ocd.geoelectric_strike = 60
ocd._rotate_to_strike = True
ocd.write_data_file()

ocm = occam.Regularization(station_locations=ocd.station_locations)
ocm.cell_width = 100
ocm.n_layers = 100
ocm.z1_layer = 10
ocm.z_target_depth = 40000
ocm.x_pad_multiplier = 1.5
ocm.num_x_pad_cells = 9
ocm.num_x_pad_small_cells = 3
ocm.build_mesh()
ocm.save_path = ocd.save_path
ocm.write_mesh_file()
ocm.build_regularization()
ocm.write_regularization_file()
ocm.plot_mesh()

ocs = occam.Startup()
ocs.data_fn = ocd.data_fn
ocs.resistivity_start = 1.7
ocs.model_fn = ocm.reg_fn
ocs.param_count = ocm.num_free_param
ocs.save_path = ocd.save_path
ocs.write_startup_file()

opr = ocd.plot_response()