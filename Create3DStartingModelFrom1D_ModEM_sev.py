# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 14:00:21 2013

@author: jpeacock-pr
"""

import mtpy.modeling.modem as modem
import mtpy.modeling.occam1d as occam1d
import numpy as np
import os
import scipy.interpolate as spi
import scipy.signal as sps

model_fn = r"c:\Users\jpeacock\Documents\folsom\inversions\inv_01\sev_modem_sm.rho"
data_fn = r"c:\Users\jpeacock\Documents\folsom\inversions\inv_01\sev_modem_data_ef07_tip03.dat"

save_dir = os.path.dirname(data_fn)
opath = "c:\\MinGW32-xy\\Peacock\\occam\\occam1d.exe"
iter_num = 4

mdd = modem.Data()
mdd.read_data_file(data_fn)

mdm = modem.Model()
mdm.read_model_file(model_fn)


new_res_model = np.zeros_like(mdm.res_model)
new_res_model[:, :, :] = 100
points = np.zeros((len(mdd.mt_dict.keys()), 2))
res_values = np.zeros((len(mdm.grid_z), len(mdd.mt_dict.keys())))

# --> compute 1D models
for dd, key in enumerate(mdd.mt_dict.keys()):
    if key == "MT008" or key == "MT013" or key == "MT014" or key == "NM04_e":
        continue

    dd_res_model = np.zeros_like(mdm.res_model)
    dd_res_model[:, :, :] = 100

    mt_obj = mdd.mt_dict[key]
    mt_obj.Z._compute_res_phase()
    rho = mt_obj.Z.resistivity
    rho_err = mt_obj.Z.resistivity_err
    phi = mt_obj.Z.phase
    phi_err = mt_obj.Z.phase_err
    rp_tup = (mt_obj.Z.freq, rho, rho_err, phi, phi_err)

    # --> write occam1d data file
    ocd = occam1d.Data()
    ocd.save_path = os.path.join(save_dir, mt_obj.station)
    ocd.write_data_file(rp_tuple=rp_tup, mode="det", res_err=10, phase_err=2.5)
    data_tm_fn = ocd.data_fn

    # --> write occam1d model file
    ocm = occam1d.Model()
    ocm.save_path = ocd.save_path
    ocm.n_layers = mdm.n_layers
    ocm.bottom_layer = mdm.grid_z[-1]
    ocm.z1_layer = mdm.grid_z[0]
    ocm.write_model_file()

    # --> write occam1d startup file
    ocs = occam1d.Startup()
    ocs.data_fn = data_tm_fn
    ocs.model_fn = ocm.model_fn
    ocs.save_path = ocd.save_path
    ocs.max_iter = 10
    ocs.write_startup_file()

    # --> run occam1d
    occam1d.Run(ocs.startup_fn, occam_path=opath, mode="Det")

    try:
        itfn = os.path.join(ocd.save_path, "Det_{0}.iter".format(iter_num))
        ocm.read_iter_file(itfn)

    except IOError:
        print "{0} did not run properly, check occam1d files".format(mt_obj.station)

    east_ii = np.where(mdm.grid_east >= mt_obj.grid_east)[0][0]
    north_jj = np.where(mdm.grid_north >= mt_obj.grid_north)[0][0]
    points[dd, 0] = mdm.grid_north[north_jj]
    points[dd, 1] = mdm.grid_east[east_ii]

    for depth, res in zip(ocm.model_depth[2:], ocm.model_res[2:]):
        if res[1] == 0.0:
            res[1] = 100

        try:
            z_kk = np.where(mdm.grid_z >= depth)[0][0]
            dd_res_model[:, :, z_kk:] = 10 ** res[1]
        except IndexError:
            pass

    new_res_model = np.sqrt(new_res_model * dd_res_model)
#            new_res_model[north_jj, east_ii, -1] = res[1]
#            res_values[-1, dd] = res[1]

## --> apply a median filter over each layer then interpolate onto grid
# mesh_north, mesh_east = np.meshgrid(mdm.grid_north, mdm.grid_east)
#
#
# res_values[np.where(res_values==0.0)] = 2.0
#
# new_res_model2 = np.zeros_like(new_res_model)
# for zz, depth_layer in enumerate(res_values):
#    depth_layer = np.nan_to_num(depth_layer)
#    gd = spi.griddata(points, 10**depth_layer, (mesh_north, mesh_east),
#                      method='nearest')
#    new_res_model2[:,:,zz] = sps.medfilt2d(gd.T, kernel_size=(7, 7))
#
# new_res_model2[np.where(new_res_model2==np.Inf)] = 100.0
# new_res_model2[np.where(new_res_model2=='-INF')] = 100.0
# new_res_model2[np.where(new_res_model2==0.0)] = 100.0
#
# for ee in range(new_res_model2.shape[0]):
#    new_res_model2[ee, :, :] = sps.medfilt2d(new_res_model2[ee, :, :],
#                                             kernel_size=(7,7))
# for nn in range(new_res_model2.shape[1]):
#    new_res_model2[:, nn, :] = sps.medfilt2d(new_res_model2[:, nn, :],
#                                             kernel_size=(7,7))
#
# new_res_model2[np.where(new_res_model2==0.0)] = 100.0


mdm.write_model_file(model_fn_basename="sev_1d_det_sm.rho", res_model=new_res_model)
