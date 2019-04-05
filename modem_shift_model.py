# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 10:19:30 2019

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from scipy import interpolate as spi
import numpy as np
from mtpy.modeling import modem

#==============================================================================
# interpolate
#==============================================================================
def interp_grid(old_model_obj, new_model_obj, shift_east=0, shift_north=0, 
                pad=1, dim='2d', smooth_kernel=None):
    """
    interpolate an old grid onto a new one
    """
    
    if dim == '2d':
        north, east = np.broadcast_arrays(old_model_obj.plot_north[:, None]+shift_north, 
                                          old_model_obj.plot_east[None, :]+shift_east)
                                          
        #2) do a 2D interpolation for each layer, much faster
        new_res = np.zeros((new_model_obj.plot_north.shape[0],
                            new_model_obj.plot_east.shape[0],
                            new_model_obj.plot_z.shape[0]))
                            
        for zz in range(new_model_obj.plot_z.shape[0]):
            try:
                old_zz = np.where(old_model_obj.plot_z >= new_model_obj.plot_z[zz])[0][0]
            except IndexError:
                old_zz = -1
                              
            print 'New depth={0:.2f}; old depth={1:.2f}'.format(new_model_obj.plot_z[zz],
                                                                old_model_obj.plot_z[old_zz])
                              
            new_res[:, :, zz] = spi.griddata((north.ravel(), east.ravel()),
                                             old_model_obj.res_model[:, :, old_zz].ravel(),
                                             (new_model_obj.plot_north[:, None], 
                                              new_model_obj.plot_east[None, :]),
                                             method='linear')
            
                               
            new_res[0:pad, pad:-pad, zz] = new_res[pad, pad:-pad, zz]    
            new_res[-pad:, pad:-pad, zz] = new_res[-pad-1, pad:-pad, zz]
            new_res[:, 0:pad, zz] = new_res[:, pad, zz].repeat(pad).reshape(
                                                      new_res[:, 0:pad, zz].shape)    
            new_res[:, -pad:, zz] = new_res[:, -pad-1, zz].repeat(pad).reshape(
                                                      new_res[:, -pad:, zz].shape)
                        
    elif dim == '3d':
        #1) first need to make x, y, z have dimensions (nx, ny, nz), similar to res
        north, east, vert = np.broadcast_arrays(old_model_obj.plot_north[:, None, None], 
                                                old_model_obj.plot_east[None, :, None], 
                                                old_model_obj.plot_z[None, None, :])
    
        #2) next interpolate ont the new mesh (3D interpolation, slow)
        new_res = spi.griddata((north.ravel(), east.ravel(), vert.ravel()),
                                old_model_obj.res_model.ravel(),
                                (new_model_obj.plot_north[:, None, None], 
                                 new_model_obj.plot_east[None, :, None], 
                                 new_model_obj.plot_z[None, None, :]),
                                 method='linear')
         
    print 'Shape of new res = {0}'.format(new_res.shape)                        
    return new_res

# =============================================================================
# Shift modem grid
# =============================================================================
mfn = r"c:\Users\jpeacock\Documents\Geysers\gz_sm50_topo_ocean.rho"
m1_obj = modem.Model()
m1_obj.read_model_file(mfn)

m2_obj = modem.Model()
m2_obj.read_model_file(mfn)

m2_obj.res_model = interp_grid(m1_obj, m2_obj, shift_east=600)
m2_obj.res_model[np.where(m1_obj.res_model < 49)] = m1_obj.res_model[np.where(m1_obj.res_model < 49)]
m2_obj.write_model_file(model_fn_basename=r"gz_sm50_topo_ocean_shifted.rho")
m2_obj.write_vtk_file(vtk_fn_basename='gz_sm_shifted_res')

### write new covariance file
cov = modem.Covariance(grid_dimensions=m2_obj.res_model.shape)
cov.write_covariance_file(save_path=m2_obj.save_path, model_fn=m2_obj.model_fn)
 
