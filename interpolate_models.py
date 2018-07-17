# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 11:41:58 2015

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import mtpy.modeling.ws3dinv as ws
import scipy.interpolate as spi
import numpy as np
import os
import time

#==============================================================================
# 
#==============================================================================

def interpolate_model_grid(old_model_fn, new_model_fn, save_path=None, 
                           new_fn_basename=None, pad=3, nan_rho=100,
                           shift_east=0, shift_north=0):
    """
    interpolate an old model onto a new model
    
    Arguments
    ------------------
        **old_model_fn** : string
                           full path to the old model file, or the file
                           that contains the original model that will be
                           interpolated onto a new grid, new_model_fn
        
        **new_model_fn** : string
                           full path to the new model file to interpolate
                           old_model_fn on to.
        
        **save_path** : string
                        directory path to save new interpolated model file
                        *default* is os.path.dirname(new_model_fn)
        
        **new_fn_basename** : string
                              filename given to the new interpolated model
                              *default* is
                              os.path.basename(new_model_fn+'interp')
                           
        **pad** : int
                  number of cells which to pad outer values of the grid.
                  Say new_model_fn is larger than old_model_fn, then there
                  will be Nan where the model don't match up, pad will 
                  extend values from the given number of cells from the edge
                  of new_model_fn.
                  
        **nan_rho** : float
                      if there are Nan in the new_model, they will be given
                      this value. *default* is 100 Ohm-m
        
        **shift_east** : float
                         shift east of new_model grid relative to the old
                         model grid in meters. *Default* is 0
        
        **shift_north** : float
                         shift north of new_model grid relative to the old
                         model grid in meters. *Default* is 0
                         
            
    """
    print 'Interpolating {0} into {1}'.format(old_model_fn, new_model_fn)
    # check to see if the old model is modem or ws    
    if old_model_fn[-4:] == '.rho':
        old_mod = modem.Model()
        old_mod.read_model_file(old_model_fn)
        
    else:
        old_mod = ws.WSModel(old_model_fn)
        old_mod.read_model_file()
        
    # check to see if the new model is modem or ws    
    if new_model_fn[-4:] == '.rho':
        new_mod = modem.Model()
        new_mod.read_model_file(new_model_fn)
        new_ext = '.rho'
        new_fn_type = 'modem'
        
    else:
        try:
            new_mod = ws.WSModel(new_model_fn)
            new_mod.read_model_file()
        except ValueError:
            new_mod = ws.WSMesh()
            new_mod.read_initial_file(new_model_fn)
        new_ext = ''
        new_fn_type = 'ws'
        
    if save_path is None:
        save_path = os.path.dirname(new_model_fn)
    
    if new_fn_basename is None:
        fn = os.path.basename(new_model_fn)
        ext_find = fn.find('.')
        if ext_find == -1:
            ext_find = len(fn)-1
        
        new_fn_basename = '{0}_interp{1}'.format(fn[0:ext_find], new_ext)
        
    print 'Start Time = {0}'.format(time.ctime())

    # make a grid of old model
    old_north, old_east = np.broadcast_arrays(old_mod.grid_north[:-1, None], 
                                              old_mod.grid_east[None, :-1])
                                      
    #2) do a 2D interpolation for each layer, much faster
    # make a new array of zeros to put values with shape of new model
    new_res = np.zeros((new_mod.nodes_north.shape[0],
                        new_mod.nodes_east.shape[0],
                        new_mod.nodes_z.shape[0]))
                        
    for zz in range(new_mod.nodes_z.shape[0]):
        try:
            old_zz = np.where(old_mod.grid_z >= new_mod.grid_z[zz])[0][0]
            if old_zz >= old_mod.nodes_z.size - 1:
                old_zz = old_mod.nodes_z.size - 1
        except IndexError:
            old_zz = -1
                          
        print 'New depth={0:.2f}; old depth={1:.2f}'.format(new_mod.grid_z[zz],
                                                            old_mod.grid_z[old_zz])
                          
        new_res[:, :, zz] = spi.griddata((old_north.ravel(), old_east.ravel()),
                                         old_mod.res_model[:, :, old_zz].ravel(),
                                         (new_mod.grid_north[:-1, None]+shift_north, 
                                          new_mod.grid_east[None, :-1]+shift_east),
                                         method='linear')
                                         
        new_res[0:pad, pad:-pad, zz] = new_res[pad, pad:-pad, zz]    
        new_res[-pad:, pad:-pad, zz] = new_res[-pad-1, pad:-pad, zz]
        new_res[:, 0:pad, zz] = new_res[:, pad, zz].repeat(pad).reshape(
                                                  new_res[:, 0:pad, zz].shape)    
        new_res[:, -pad:, zz] = new_res[:, -pad-1, zz].repeat(pad).reshape(
                                                  new_res[:, -pad:, zz].shape)
                                            
                             
    
    #
    new_res[np.where(np.nan_to_num(new_res)==0.0)] = 100.0
    
    if new_fn_type == 'modem':
        new_mod.write_model_file(save_path=save_path,
                                   model_fn_basename=new_fn_basename,
                                   res_model=new_res)
    else:
        nfid = file(os.path.join(save_path, new_fn_basename), 'w')
        nfid.write('# interpolated starting model for ws written by mtpy\n')
        nfid.write('{0} {1} {2} {3}\n'.format(new_mod.nodes_north.shape[0],
                                              new_mod.nodes_east.shape[0],
                                              new_mod.nodes_z.shape[0],
                                              0))
        # write S--> N block
        for ii, n_node in enumerate(new_mod.nodes_north):
            nfid.write('{0:>12.1f}'.format(abs(n_node)))
            if ii != 0 and np.remainder(ii+1, 5) == 0:
                nfid.write('\n')
            elif ii == new_mod.nodes_north.shape[0]-1:
                nfid.write('\n')
        # write W--> E block
        for jj, e_node in enumerate(new_mod.nodes_east):
            nfid.write('{0:>12.1f}'.format(abs(e_node)))
            if jj != 0 and np.remainder(jj+1, 5) == 0:
                nfid.write('\n')
            elif jj == new_mod.nodes_east.shape[0]-1:
                nfid.write('\n')
        # write top--> bottom block
        for kk, z_node in enumerate(new_mod.nodes_z):
            nfid.write('{0:>12.1f}'.format(abs(z_node)))
            if kk != 0 and np.remainder(kk+1, 5) == 0:
                nfid.write('\n')
            elif kk == new_mod.nodes_z.shape[0]-1:
                nfid.write('\n')
        
        for kk in range(new_mod.nodes_z.shape[0]):
            for jj in range(new_mod.nodes_east.shape[0]):
                for ii in range(new_mod.nodes_north.shape[0]):
                    nfid.write('{0:.4e}\n'.format(
                                 new_res[(new_mod.nodes_north.shape[0]-1)-ii,
                                 jj, kk]))
        nfid.close()
        print 'Wrote file to {0}'.format(os.path.join(save_path, new_fn_basename))
                
#        new_mesh = ws.WSMesh()
#        new_mesh.write_initial_file(nodes_north=new_mod.nodes_north,
#                                    nodes_east=new_mod.nodes_east,
#                                    nodes_z=new_mod.nodes_z,/home/jpeacock/Documents/ModEM/LV/geo_err12/lv_geo_err03_cov5_NLCG_065.res
#                                    res_model=new_res,
#                                    save_path=save_path)
        
    print 'End Time = {0}'.format(time.ctime())
    return os.path.join(save_path, new_fn_basename)                           
#==============================================================================
# 
#==============================================================================
#deep_fn = r"/home/jpeacock/Documents/wsinv3d/LV/geothermal_deep_02/lv_geo_deep_fine_model.04"
#shallow_fn = r"/home/jpeacock/Documents/wsinv3d/LV/geothermal_shallow/WSInitialMesh500m_shallow"
#interpolate_model_grid(deep_fn, shallow_fn, pad=3)

#ws_fn = r"/home/jpeacock/Documents/wsinv3d/LV/geothermal_shallow/lv_geo_shallow_model.07"
#modem_fn = r"/home/jpeacock/Documents/ModEM/LV/geo_err12/lv_geo_err12_cov5_NLCG_037.rho"
#interpolate_model_grid(ws_fn, modem_fn, pad=5, new_fn_basename='lv_ws_sm.rho',
#                       shift_east = 4500, shift_north = 1700)

mod_fn_old = r"c:\Users\jpeacock\Documents\SaudiArabia\inversions\inv_02\sa_t02_049.rho"
mod_fn_new = r"c:\Users\jpeacock\Documents\SaudiArabia\inversions\inv_03\sa_sm02.rho"
interpolate_model_grid(mod_fn_old,
                       mod_fn_new, 
                       new_fn_basename='sa_sm_zt.rho',
                       pad=3)