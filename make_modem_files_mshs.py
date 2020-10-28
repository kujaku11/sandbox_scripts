# -*- coding: utf-8 -*-
"""
Created on Wed May 25 17:17:14 2016

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os
import numpy as np

# save_path = r"c:\Users\jpeacock\Documents\ShanesBugs\Sev_MT_Final_ga"
# s_edi_path = r"c:\Users\jpeacock\Documents\ShanesBugs\Sev_MT_Final_ga\inv_edi_files"
# s_list = ['MT{0:03}.edi'.format(ii) for ii in range(0, 12)]
save_path = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\modem_inv"
edi_path = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\EDI_Files_INV"

s_edi_list = [
    os.path.join(edi_path, ss) for ss in os.listdir(edi_path) if ss.endswith(".edi")
]

# make mesh first
mod_obj = modem.Model(edi_list=s_edi_list)
mod_obj.cell_size_east = 200
mod_obj.cell_size_north = 200
mod_obj.pad_east = 18
mod_obj.pad_north = 18
mod_obj.pad_stretch_h = 1.4
mod_obj.pad_z = 4
mod_obj.n_layers = 40
mod_obj.z_target_depth = 40000.0

mod_obj.make_mesh()
mod_obj.plot_mesh()

mod_obj.write_model_file(model_fn=os.path.join(save_path, r"mshs_modem_sm.rho"))

inv_period_list = np.logspace(-np.log10(625.0), 3, num=23)
data_obj = modem.Data(
    edi_list=s_edi_list,
    station_locations=mod_obj.station_locations,
    period_list=inv_period_list,
)
data_obj.error_type = "egbert"
data_obj.error_egbert = 10.0
data_obj.error_tipper = 0.05
data_obj.get_mt_dict()
data_obj._fill_data_array()
data_obj.data_array["elev"][:] = 0.0
data_obj.write_data_file(
    save_path=save_path, fn_basename="mshs_modem_data_err10_old.dat"
)

cov = modem.Covariance(grid_dimensions=mod_obj.res_model.shape)
cov.smoothing_east = 0.4
cov.smoothing_north = 0.4
cov.smoothing_z = 0.4

cov.write_covariance_file(os.path.join(save_path, "covariance_old.cov"))
