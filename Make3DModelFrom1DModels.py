# -*- coding: utf-8 -*-
"""
Created on Tue Dec 03 13:18:41 2013

@author: jpeacock-pr
"""

import mtpy.modeling.ws3dinv as ws
import mtpy.modeling.occam1d as occam1d
import numpy as np
import os
import scipy.interpolate as spi
import scipy.signal as sps

#==============================================================================
# Inputs
#==============================================================================
save_path = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\EDI_1DInversions"
edi_path = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_MT\EDI_1DInversions\EDI_Files"

cell_size_east = 500
cell_size_north = 500

z1_thickness = 5
z_depth = 300000

n_layers = 45
res_err = 30
phase_err = 2.5
max_iter = 20
iter_num = 5

edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.find('.edi')>0]

#==============================================================================
#  get station locations
#==============================================================================
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.find('.edi')>0]

wsm = ws.WSMesh()
wsm.edi_list = edi_list
wsm.cell_size_east = cell_size_east
wsm.cell_size_north = cell_size_north
wsm.pad_root_east = 5
wsm.pad_root_north = 5
wsm.pad_east = 10
wsm.pad_north = 10
wsm.z1_layer = z1_thickness
wsm.z_bottom = z_depth
wsm.z_target_depth = 50000
wsm.n_layers = n_layers
wsm.save_path = save_path
wsm.make_mesh()
wsm.write_initial_file()

model_shape = (wsm.grid_north.shape[0],
               wsm.grid_east.shape[0], 
               wsm.grid_z.shape[0])

res_grid_te = np.zeros(model_shape)
                        
res_grid_tm = np.zeros(model_shape)    

wss = ws.WSStation()
wss.read_station_file(os.path.join(save_path, 'WS_Station_Locations.txt'))

new_res_model = np.zeros(model_shape)
points = np.zeros((len(edi_list), 2))
res_values_te = np.zeros((len(wsm.grid_z), len(edi_list)))
res_values_tm = np.zeros((len(wsm.grid_z), len(edi_list)))

#--> fill resistivity values with those from the 1D models
for ss, station in enumerate(os.listdir(save_path)):
    if station == 'EDI_Files' :
        pass
    
    elif os.path.isdir(os.path.join(save_path, station)) == True:
        try:
            station_ss = np.where(wss.names == station.upper())[0][0]
            east_jj = np.where(wsm.grid_east >= wss.east[station_ss])[0][0]
            north_ii = np.where(wsm.grid_north >= wss.north[station_ss])[0][0]
            points[ss, 0] = wsm.grid_north[north_ii]
            points[ss, 1] = wsm.grid_east[east_jj] 
            
            try:
                ocm = occam1d.Model()
                ocm.model_fn = os.path.join(save_path, station, 'Model1D')
                ocm.read_iter_file(os.path.join(save_path, station, 
                                    '{0}_{1}.iter'.format('TE', iter_num)))
                for depth, res in zip(ocm.model_depth[2:], ocm.model_res[2:]):
                    z_kk = np.where(wsm.grid_z >= depth)[0][0]
                    res_grid_te[north_ii, east_jj, z_kk] = res[1]
                    res_values_te[z_kk, ss] = res[1]
            except IOError:
                print 'Could not find {0}_{1}.iter for {2}'.format('TE', 
                                                                   iter_num,
                                                                   station)
            try:
                ocm = occam1d.Model()
                ocm.model_fn = os.path.join(save_path, station, 'Model1D')
                ocm.read_iter_file(os.path.join(save_path, station, 
                                    '{0}_{1}.iter'.format('TM', iter_num)))
                for depth, res in zip(ocm.model_depth[2:], ocm.model_res[2:]):
                    z_kk = np.where(wsm.grid_z >= depth)[0][0]
                    res_grid_tm[north_ii, east_jj, z_kk] = res[1]
                    res_values_tm[z_kk, ss] = res[1]
            except IOError:
                print 'Could not find {0}_{1}.iter for {2}'.format('TM', 
                                                                   iter_num,
                                                                   station)
        except IndexError:
            print 'Could not find station {0}'.format(station)
                                                               
                                                               
#--> Interpolate and apply a median filter to the model to smooth it out
mesh_north, mesh_east = np.meshgrid(wsm.grid_north, wsm.grid_east)        

te_model = np.zeros(model_shape)    
for zz, depth_layer in enumerate(res_values_te):
    depth_layer = np.nan_to_num(depth_layer)
    gd = spi.griddata(points, 10**depth_layer, (mesh_north, mesh_east), 
                      method='nearest')
    te_model[:,:,zz] = sps.medfilt2d(gd.T, kernel_size=(15, 15))
tm_model = np.zeros(model_shape)    
for zz, depth_layer in enumerate(res_values_tm):
    depth_layer = np.nan_to_num(depth_layer)
    gd = spi.griddata(points, 10**depth_layer, (mesh_north, mesh_east), 
                      method='nearest')
    tm_model[:,:,zz] = sps.medfilt2d(gd.T, kernel_size=(11, 11))

res_list = [1, 50, 100, 500, 1000, 1000] 
res_dict = dict([(res, ii) for ii, res in enumerate(res_list,1)])  

#make values in model resistivity array a value in res_list
resm_te = np.ones(model_shape)
resm_te[np.where(te_model < res_list[0])] =  res_dict[res_list[0]]
resm_te[np.where(te_model) > res_list[-1]] = res_dict[res_list[-1]]

resm_tm = np.ones(model_shape)
resm_tm[np.where(tm_model < res_list[0])] =  res_dict[res_list[0]]
resm_tm[np.where(tm_model) > res_list[-1]] = res_dict[res_list[-1]]

for zz in range(model_shape[2]):
    for yy in range(model_shape[1]):
        for xx in range(model_shape[0]):
            for rr in range(len(res_list)-1):
                if te_model[xx, yy, zz] >= res_list[rr] and \
                   te_model[xx, yy, zz] <= res_list[rr+1]:
                    resm_te[xx, yy, zz] = res_dict[res_list[rr]]
                    break
                elif te_model[xx, yy, zz] <= res_list[0]:
                    resm_te[xx, yy, zz] = res_dict[res_list[0]]
                    break
                elif te_model[xx, yy, zz] >= res_list[-1]:
                    resm_te[xx, yy, zz] = res_dict[res_list[-1]]
                    break
                
for zz in range(model_shape[2]):
    for yy in range(model_shape[1]):
        for xx in range(model_shape[0]):
            for rr in range(len(res_list)-1):
                if tm_model[xx, yy, zz] >= res_list[rr] and \
                   tm_model[xx, yy, zz] <= res_list[rr+1]:
                    resm_tm[xx, yy, zz] = res_dict[res_list[rr]]
                    break
                elif tm_model[xx, yy, zz] <= res_list[0]:
                    resm_tm[xx, yy, zz] = res_dict[res_list[0]]
                    break
                elif tm_model[xx, yy, zz] >= res_list[-1]:
                    resm_tm[xx, yy, zz] = res_dict[res_list[-1]]
                    break
                
#need to fill out the padding cells, cause the median filter basically sets 
# them to 0
for zz in range(model_shape[2]):
    for yy in range(model_shape[1]):
        resm_tm[0:wsm.pad_east, yy, zz] = resm_tm[wsm.pad_east+1, yy, zz]
        resm_tm[-wsm.pad_east:, yy, zz] = resm_tm[-wsm.pad_east-1, yy, zz]
        resm_te[0:wsm.pad_east, yy, zz] = resm_te[wsm.pad_east+1, yy, zz]
        resm_te[-wsm.pad_east:, yy, zz] = resm_te[-wsm.pad_east-1, yy, zz]
    for xx in range(model_shape[0]):
        resm_tm[xx, 0:wsm.pad_north, zz] = resm_tm[xx, wsm.pad_north+1, zz]
        resm_tm[xx, -wsm.pad_north:, zz] = resm_tm[xx, -wsm.pad_north-1, zz]  
        resm_te[xx, 0:wsm.pad_north, zz] = resm_te[xx, wsm.pad_north+1, zz]
        resm_te[xx, -wsm.pad_north:, zz] = resm_te[xx, -wsm.pad_north-1, zz]  
            

#--> need to flip the array about the north axis because ws assumes the first
#    index is the northermost grid cell, but here it is the last
wsm.res_list = res_list
wsm.res_model = resm_te
wsm.initial_fn = os.path.join(save_path, 'WSInputModel_1D_te')
wsm.write_initial_file(res_list=res_list, res_model=resm_te[::-1, :, :]) 
wsm.initial_fn = os.path.join(save_path, 'WSInputModel_1D_tm')                                                             
wsm.write_initial_file(res_list=res_list, res_model=resm_tm[::-1, :, :])                                                              
                                                               
                                                               
            

            
            
            
