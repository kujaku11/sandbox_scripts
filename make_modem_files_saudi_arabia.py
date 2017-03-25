# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 17:20:17 2016

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import os
import numpy as np

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\Edited"
inv_save_path = r"c:\Users\jpeacock\Documents\SaudiArabia\inversions"

inv_period_list = np.logspace(np.log10(0.003125),
                              np.log10(10922.),
                              num=23)

s_edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
              if edi.endswith('.edi')]
            

# make mesh first
mod_obj = modem.Model(edi_list=s_edi_list)
mod_obj.cell_size_east = 2000.
mod_obj.cell_size_north = 2000.
mod_obj.pad_east = 14
mod_obj.pad_north = 14
mod_obj.pad_stretch_h = 1.2
mod_obj.pad_stretch_v = 1.4
mod_obj.pad_z = 5
mod_obj.n_layers = 50
mod_obj.z_target_depth = 70000.
mod_obj.mesh_rotation_angle = 30

mod_obj.make_mesh()
mod_obj.plot_mesh()

mod_obj.write_model_file(model_fn=os.path.join(inv_save_path,
                                               r"sa_modem_sm.rho"))

## --> write data file
md = modem.Data(edi_list=s_edi_list,
                station_locations=mod_obj.station_locations,
                period_list=inv_period_list)
md.rotation_angle = 0.0
md.error_type = 'floor_egbert'
md.error_egbert = 3.0
md.error_tipper = .03
md.write_data_file(save_path=inv_save_path,
                   fn_basename='sa_modem_data_err03_tip03_n30w.dat')

cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4

cov.write_covariance_file(os.path.join(inv_save_path, 'covariance.cov'))