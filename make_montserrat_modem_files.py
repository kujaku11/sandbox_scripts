# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 10:31:45 2016

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import os
import numpy as np


# ==============================================================================
# Inputs
# ==============================================================================
edi_path = r"c:\Users\jpeacock\Documents\Montserrat\EDI_Montserrat\Edited\DR"
save_path = r"c:\Users\jpeacock\Documents\Montserrat\modem_inv\Inv04_dr"

fn_stem = "mont"
s_edi_list = [
    os.path.join(edi_path, ss) for ss in os.listdir(edi_path) if ss.endswith(".edi")
]

if not os.path.exists(save_path):
    os.mkdir(save_path)

# shift_x = 2579.666
# shift_y = 2305.41
# shift_z = 612
# ==============================================================================
# Make the data file
# ==============================================================================
inv_period_list = np.logspace(-np.log10(500), np.log10(1572), num=23)
data_obj = modem.Data(edi_list=s_edi_list, period_list=inv_period_list)

data_obj.error_type_z = "eigen_floor"
data_obj.error_value_z = 10.0
data_obj.inv_mode = "1"

data_obj.error_value_tipper = 0.05
data_obj.error_type_tipper = "abs_floor"

# data_obj.get_mt_dict()
# data_obj.fill_data_array()
# data_obj.compute_inv_error()
# data_obj.get_relative_station_locations()
#
# data_obj.data_array['rel_north'][:] += shift_x
# data_obj.data_array['rel_east'][:] += shift_y
# data_obj.data_array['elev'][:] += shift_z

# --> here is where you can rotate the data
data_obj.write_data_file(
    save_path=save_path,
    fn_basename="{1}_modem_data_err{0:02.0f}_tip{2:02.0f}.dat".format(
        data_obj.error_value_z, fn_stem, data_obj.error_value_tipper * 100
    ),
    elevation=True,
    fill=True,
    compute_error=True,
)


# ==============================================================================
# Write model file
# ==============================================================================
mod_obj = modem.Model(data_obj.station_locations)
mod_obj.cell_size_east = 150
mod_obj.cell_size_north = 150
mod_obj.ew_ext = 300000
mod_obj.ns_ext = 300000
mod_obj.pad_east = 10
mod_obj.pad_north = 10
mod_obj.z1_layer = 30
mod_obj.z_target_depth = 25000
mod_obj.z_bottom = 300000
mod_obj.n_layers = 40

mod_obj.make_mesh()
mod_obj.plot_mesh()

mod_obj.write_model_file(save_path=save_path, model_fn_basename="mont_base.rho")


#
# cov = modem.Covariance(grid_dimensions=m_obj.res_model.shape)
# cov.smoothing_east = .4
# cov.smoothing_north = .4
# cov.smoothing_z = .4
# cov.save_path = m_obj.save_path
# cov.write_covariance_file()
