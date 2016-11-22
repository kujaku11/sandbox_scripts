# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 14:00:21 2013

@author: jpeacock-pr
"""

import mtpy.modeling.ws3dinv as ws
import mtpy.modeling.occam1d as occam1d
import numpy as np
import matplotlib.pyplot as plt
import mtpy.core.z as mtz
import os
import scipy.interpolate as spi
import scipy.signal as sps

#data_fn = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\Inv1_bigger\WSDataFile_small.dat"
#model_fn = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\Inv1_bigger\WSInitialModel"
#station_fn = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\Inv1_bigger\WS_Station_Locations.txt"
data_fn = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\WS3D_Inv1\WSDataFile.dat"
model_fn = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\WS3D_Inv1\WSInitialModel_small"
station_fn = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\WS3D_Inv1\WS_Station_Locations.txt"

save_dir = os.path.dirname(data_fn)
opath = 'c:\\MinGW32-xy\\Peacock\\occam\\occam1d.exe'
iter_num = 6 

wsd = ws.WSData()
wsd.read_data_file(data_fn, station_fn=station_fn)

wsm = ws.WSMesh()
wsm.read_initial_file(model_fn)


new_res_model = np.zeros_like(wsm.res_model)
points = np.zeros((len(wsd.data), 2))
res_values = np.zeros((len(wsm.grid_z), len(wsd.data)))

#--> compute 1D models 
for dd, data in enumerate(wsd.data):
    z_object = mtz.Z(z_array=data['z_data'], zerr_array=data['z_data_err'],
                     freq=1./wsd.period_list)
    rho = z_object.resistivity
    rho_err = z_object.resistivity_err
    phi = z_object.phase
    phi_err = z_object.phase_err
    rp_tup = (z_object.freq, rho, rho_err, phi, phi_err)

    #--> write occam1d data file             
    ocd = occam1d.Data()
    ocd.save_path = os.path.join(save_dir, data['station'])
    ocd.write_data_file(rp_tuple=rp_tup, mode='TM', res_err=10, phase_err=2.5)
    data_tm_fn = ocd.data_fn    
    ocd.write_data_file(rp_tuple=rp_tup, mode='TE', res_err=10, phase_err=2.5)
    data_te_fn = ocd.data_fn
    
    #--> write occam1d model file
    ocm = occam1d.Model()
    ocm.save_path = ocd.save_path
    ocm.n_layers = wsm.n_layers
    ocm.bottom_layer = wsm.grid_z[-1]
    ocm.z1_layer = wsm.grid_z[0]
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
    
    #--> write occam1d startup file
    ocs = occam1d.Startup()
    ocs.data_fn = data_te_fn
    ocs.model_fn = ocm.model_fn
    ocs.save_path = ocd.save_path
    ocs.max_iter = 10
    ocs.write_startup_file()
    occam1d.Run(ocs.startup_fn, occam_path=opath, mode='TE')
    
    try:
        itfn = os.path.join(ocd.save_path, 'TE_{0}.iter'.format(iter_num))
        ocm.read_iter_file(itfn)
        resp_tm_list = [os.path.join(ocd.save_path, 'TM_{0}.resp'.format(rr))
                     for rr in range(1, iter_num+1)]
        iter_tm_list = [os.path.join(ocd.save_path, 'TM_{0}.iter'.format(rr))
                     for rr in range(1, iter_num+1)]
        resp_te_list = [os.path.join(ocd.save_path, 'TE_{0}.resp'.format(rr))
                     for rr in range(1, iter_num+1)]
        iter_te_list = [os.path.join(ocd.save_path, 'TE_{0}.iter'.format(rr))
                     for rr in range(1, iter_num+1)]
        model_fn = os.path.join(ocd.save_path, 'Model1D')
        p1 = occam1d.Plot1DResponse(data_tm_fn=data_tm_fn,
                                    data_te_fn=data_te_fn,
                                    model_fn=model_fn,
                                    resp_tm_fn=resp_tm_list[-1],
                                    iter_tm_fn=iter_tm_list[-1],
                                    resp_te_fn=resp_te_list[-1],
                                    iter_te_fn=iter_te_list[-1],
                                    depth_limits=(0, 50))
                                    
        sv_path = os.path.join(save_dir, 'Plots', data['station']+'.png')
        p1.save_figure(sv_path, fig_dpi=600)
    except IOError:
        print '{0} did not run properly, check occam1d files'.format(data['station'])
    
    
    
    
    east_ii = np.where(wsm.grid_east >= data['east'])[0][0]
    north_jj = np.where(wsm.grid_north >= data['north'])[0][0]
    points[dd, 0] = wsm.grid_north[north_jj]
    points[dd, 1] = wsm.grid_east[east_ii] 
    
    
    for depth, res in zip(ocm.model_depth[2:], ocm.model_res[2:]):
        z_kk = np.where(wsm.grid_z >= depth)[0][0]
        new_res_model[north_jj, east_ii, z_kk] = res[1]
        res_values[z_kk, dd] = res[1]
        
# --> apply a median filter over each layer then interpolate onto grid
mesh_north, mesh_east = np.meshgrid(wsm.grid_north, wsm.grid_east)        

new_res_model2 = np.zeros_like(new_res_model)     
for zz, depth_layer in enumerate(res_values):
    depth_layer = np.nan_to_num(depth_layer)
    gd = spi.griddata(points, 10**depth_layer, (mesh_north, mesh_east), 
                      method='nearest')
    new_res_model2[:,:,zz] = sps.medfilt2d(gd.T, kernel_size=(7, 7))

for ee in range(new_res_model2.shape[0]):
    new_res_model2[ee, :, :] = sps.medfilt2d(new_res_model2[ee, :, :], 
                                             kernel_size=(7,7))
for nn in range(new_res_model2.shape[1]):
    new_res_model2[:, nn, :] = sps.medfilt2d(new_res_model2[:, nn, :], 
                                             kernel_size=(7,7))

res_list = [1, 50, 100, 500, 1000, 1000] 
res_dict = dict([(res, ii) for ii, res in enumerate(res_list,1)])  

#make values in model resistivity array a value in res_list
resm = np.ones_like(wsm.res_model)
resm[np.where(new_res_model2 < res_list[0])] =  res_dict[res_list[0]]
resm[np.where(new_res_model2) > res_list[-1]] = res_dict[res_list[-1]]

for zz in range(new_res_model2.shape[2]):
    for yy in range(new_res_model2.shape[1]):
        for xx in range(new_res_model2.shape[0]):
            for rr in range(len(res_list)-1):
                if new_res_model2[xx, yy, zz] >= res_list[rr] and \
                   new_res_model2[xx, yy, zz] <= res_list[rr+1]:
                    resm[xx, yy, zz] = res_dict[res_list[rr]]
                    break
                elif new_res_model2[xx, yy, zz] <= res_list[0]:
                    resm[xx, yy, zz] = res_dict[res_list[0]]
                    break
                elif new_res_model2[xx, yy, zz] >= res_list[-1]:
                    resm[xx, yy, zz] = res_dict[res_list[-1]]
                    break
                
wsm.res_list = res_list
wsm.res_model = resm
wsm.initial_fn = model_fn+'_1D'
wsm.write_initial_file(res_list=res_list, res_model=resm)

        
    
    
    