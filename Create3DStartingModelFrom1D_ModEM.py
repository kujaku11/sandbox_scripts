# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 14:00:21 2013

@author: jpeacock-pr
"""

import mtpy.modeling.ws3dinv as ws
import mtpy.modeling.modem_new as modem
import mtpy.modeling.occam1d as occam1d
import numpy as np
import matplotlib.pyplot as plt
import mtpy.core.z as mtz
import os
import scipy.interpolate as spi
import scipy.signal as sps

model_fn = r"c:\MinGW32-xy\Peacock\ModEM\Test_04\ModeEM_Model_rw.ws"
data_fn = r"c:\MinGW32-xy\Peacock\ModEM\Test_04\ModEM_Data.dat"

save_dir = os.path.dirname(data_fn)
opath = 'c:\\MinGW32-xy\\Peacock\\occam\\occam1d.exe'
iter_num = 6 

mdd = modem.Data()
mdd.read_data_file(data_fn)

mdm = modem.Model()
mdm.read_model_file(model_fn)


new_res_model = np.zeros_like(mdm.res_model)
points = np.zeros((len(mdd.mt_dict.keys()), 2))
res_values = np.zeros((len(mdm.grid_z), len(mdd.mt_dict.keys())))

#--> compute 1D models 
for dd, key in enumerate(mdd.mt_dict.keys()):
    if key == 'MB129' or key == 'MB040' or key == 'MB054' or key == 'MB072' or\
       key == 'MB111' or key == 'MB115' or key == 'MB130' or key == 'MB018':
        pass
    else:
        mt_obj = mdd.mt_dict[key]
        mt_obj.Z._compute_res_phase()
        rho = mt_obj.Z.resistivity
        rho_err = mt_obj.Z.resistivity_err
        phi = mt_obj.Z.phase
        phi_err = mt_obj.Z.phase_err
        rp_tup = (mt_obj.Z.freq, rho, rho_err, phi, phi_err)
    
        #--> write occam1d data file             
        ocd = occam1d.Data()
        ocd.save_path = os.path.join(save_dir, mt_obj.station)
        ocd.write_data_file(rp_tuple=rp_tup, mode='TM', res_err=10, phase_err=2.5)
        data_tm_fn = ocd.data_fn    
    #    ocd.write_data_file(rp_tuple=rp_tup, mode='TE', res_err=10, phase_err=2.5)
    #    data_te_fn = ocd.data_fn
        
        #--> write occam1d model file
        ocm = occam1d.Model()
        ocm.save_path = ocd.save_path
        ocm.n_layers = mdm.n_layers
        ocm.bottom_layer = mdm.grid_z[-1]
        ocm.z1_layer = mdm.grid_z[0]
        ocm.write_model_file()
        
        #--> write occam1d startup file
        ocs = occam1d.Startup()
        ocs.data_fn = data_tm_fn
        ocs.model_fn = ocm.model_fn
        ocs.save_path = ocd.save_path
        ocs.max_iter = 10
        ocs.write_startup_file()
        
        #--> run occam1d
        occam1d.Run(ocs.startup_fn, occam_path=opath, mode='TM')
        
    #    #--> write occam1d startup file
    #    ocs = occam1d.Startup()
    #    ocs.data_fn = data_te_fn
    #    ocs.model_fn = ocm.model_fn
    #    ocs.save_path = ocd.save_path
    #    ocs.max_iter = 10
    #    ocs.write_startup_file()
    #    occam1d.Run(ocs.startup_fn, occam_path=opath, mode='TE')
        
        try:
            itfn = os.path.join(ocd.save_path, 'TM_{0}.iter'.format(iter_num))
            ocm.read_iter_file(itfn)
#            resp_tm_list = [os.path.join(ocd.save_path, 'TM_{0}.resp'.format(rr))
#                         for rr in range(1, iter_num+1)]
#            iter_tm_list = [os.path.join(ocd.save_path, 'TM_{0}.iter'.format(rr))
#                         for rr in range(1, iter_num+1)]
##            resp_te_list = [os.path.join(ocd.save_path, 'TE_{0}.resp'.format(rr))
##                         for rr in range(1, iter_num+1)]
##            iter_te_list = [os.path.join(ocd.save_path, 'TE_{0}.iter'.format(rr))
##                         for rr in range(1, iter_num+1)]
#            model_fn = os.path.join(ocd.save_path, 'Model1D')
##            p1 = occam1d.Plot1DResponse(data_tm_fn=data_tm_fn,
##                                        data_te_fn=data_te_fn,
##                                        model_fn=model_fn,
##                                        resp_tm_fn=resp_tm_list[-1],
##                                        iter_tm_fn=iter_tm_list[-1],
##                                        resp_te_fn=resp_te_list[-1],
##                                        iter_te_fn=iter_te_list[-1],
##                                        depth_limits=(0, 50))
#            p1 = occam1d.Plot1DResponse(data_tm_fn=data_tm_fn,
#                                        model_fn=model_fn,
#                                        resp_tm_fn=resp_tm_list[-1],
#                                        iter_tm_fn=iter_tm_list[-1],
#                                        depth_limits=(0, 50))
#                                        
#            sv_path = os.path.join(save_dir, 'Plots', mt_obj.station+'.png')
#            p1.save_figure(sv_path, fig_dpi=600)
        except IOError:
            print '{0} did not run properly, check occam1d files'.format(mt_obj.station)
        
    
        east_ii = np.where(mdm.grid_east >= mt_obj.grid_east)[0][0]
        north_jj = np.where(mdm.grid_north >= mt_obj.grid_north)[0][0]
        points[dd, 0] = mdm.grid_north[north_jj]
        points[dd, 1] = mdm.grid_east[east_ii] 
        
        
        for depth, res in zip(ocm.model_depth[2:], ocm.model_res[2:]):
            if res[1] == 0.0:
                res[1] = 2
            
            try:
                z_kk = np.where(mdm.grid_z >= depth)[0][0]
                new_res_model[north_jj, east_ii, z_kk] = res[1]
                res_values[z_kk, dd] = res[1]
            except IndexError:
                new_res_model[north_jj, east_ii, -1] = res[1]
                res_values[-1, dd] = res[1]
            
# --> apply a median filter over each layer then interpolate onto grid
mesh_north, mesh_east = np.meshgrid(mdm.grid_north, mdm.grid_east)  

      
res_values[np.where(res_values==0.0)] = 2.0

new_res_model2 = np.zeros_like(new_res_model)     
for zz, depth_layer in enumerate(res_values):
    depth_layer = np.nan_to_num(depth_layer)
    gd = spi.griddata(points, 10**depth_layer, (mesh_north, mesh_east), 
                      method='nearest')
    new_res_model2[:,:,zz] = sps.medfilt2d(gd.T, kernel_size=(7, 7))

new_res_model2[np.where(new_res_model2==np.Inf)] = 100.0
new_res_model2[np.where(new_res_model2=='-INF')] = 100.0
new_res_model2[np.where(new_res_model2==0.0)] = 100.0

for ee in range(new_res_model2.shape[0]):
    new_res_model2[ee, :, :] = sps.medfilt2d(new_res_model2[ee, :, :], 
                                             kernel_size=(7,7))
for nn in range(new_res_model2.shape[1]):
    new_res_model2[:, nn, :] = sps.medfilt2d(new_res_model2[:, nn, :], 
                                             kernel_size=(7,7))
                                             
new_res_model2[np.where(new_res_model2==0.0)] = 100.0


                                             
mdm.model_fn = model_fn+'_1D'
mdm.write_model_file(model_fn_basename='ModEM_Start_1D_TM', 
                     res_model=new_res_model2)

        
    
    
    