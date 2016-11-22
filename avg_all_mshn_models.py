# -*- coding: utf-8 -*-
"""
Created on Mon Jan 12 13:43:30 2015

Average all existing model of long valley

@author: jpeacock
"""
import os
import numpy as np
import mtpy.modeling.ws3dinv as ws
import mtpy.modeling.modem_new as modem
import matplotlib.pyplot as plt
import scipy.signal as sps
import scipy.interpolate as spi

def smooth_2d(res_array, window_len):
    """
    convolve a gaussian window for smoothing
    """
    
    gx, gy = np.mgrid[-window_len:window_len+1, 
                      -window_len:window_len+1]
                      
    gauss = np.exp(-(gx**2/float(window_len)+gy**2/float(window_len)))
    gauss /= gauss.sum()
    
    smooth_array = sps.convolve(res_array, gauss, mode='same')
    
    return smooth_array


def interp_grid(old_model_obj, new_model_obj, shift_east=0, shift_north=0, 
                pad=1, dim='2d', smooth_kernel=None):
    """
    interpolate an old grid onto a new one
    """
    
    if dim == '2d':
        north, east = np.broadcast_arrays(old_model_obj.grid_north[:, None]+shift_north, 
                                          old_model_obj.grid_east[None, :]+shift_east)
                                          
        #2) do a 2D interpolation for each layer, much faster
        new_res = np.zeros((new_model_obj.grid_north.shape[0],
                            new_model_obj.grid_east.shape[0],
                            new_model_obj.grid_z.shape[0]))
                            
        for zz in range(new_model_obj.grid_z.shape[0]):
            try:
                old_zz = np.where(old_model_obj.grid_z >= new_model_obj.grid_z[zz])[0][0]
            except IndexError:
                old_zz = -1
                              
            print 'New depth={0:.2f}; old depth={1:.2f}'.format(new_model_obj.grid_z[zz],
                                                                old_model_obj.grid_z[old_zz])
                              
            new_res[:, :, zz] = spi.griddata((north.ravel(), east.ravel()),
                                             old_model_obj.res_model[:, :, old_zz].ravel(),
                                             (new_model_obj.grid_north[:, None], 
                                              new_model_obj.grid_east[None, :]),
                                             method='linear')
            
            
                                             
            new_res[0:pad, pad:-pad, zz] = new_res[pad, pad:-pad, zz]    
            new_res[-pad:, pad:-pad, zz] = new_res[-pad-1, pad:-pad, zz]
            new_res[:, 0:pad, zz] = new_res[:, pad, zz].repeat(pad).reshape(
                                                      new_res[:, 0:pad, zz].shape)    
            new_res[:, -pad:, zz] = new_res[:, -pad-1, zz].repeat(pad).reshape(
                                                      new_res[:, -pad:, zz].shape)
                                                      
            if smooth_kernel is not None:
                new_res[:, :, zz] = smooth_2d(new_res[:, :, zz], smooth_kernel)
                        
    elif dim == '3d':
        #1) first need to make x, y, z have dimensions (nx, ny, nz), similar to res
        north, east, vert = np.broadcast_arrays(old_model_obj.grid_north[:, None, None], 
                                                old_model_obj.grid_east[None, :, None], 
                                                old_model_obj.grid_z[None, None, :])
    
        #2) next interpolate ont the new mesh (3D interpolation, slow)
        new_res = spi.griddata((north.ravel(), east.ravel(), vert.ravel()),
                                old_model_obj.res_model.ravel(),
                                (new_model_obj.grid_north[:, None, None], 
                                 new_model_obj.grid_east[None, :, None], 
                                 new_model_obj.grid_z[None, None, :]),
                                 method='linear')
         
    print 'Shape of new res = {0}'.format(new_res.shape)                        
    return new_res
            
#==============================================================================
#  interpolate all models onto the same grid
#==============================================================================
dir_path = r'c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions'
data_fn = os.path.join(dir_path, 'mshn_modem_data_ef05.dat')
mfn_tipper = os.path.join(dir_path, r"mshn_tip_err03_NLCG_050.rho")
mfn_ws_sm2 = os.path.join(dir_path, r"mshn_sm2_fine_model.05")
mfn_ws_sm3 = os.path.join(dir_path, r"mshn_sm3_fine_model.04")
mfn_all_sm500 = os.path.join(dir_path, r"mshn_err05_cov03_NLCG_063.rho")


#difference between modem and ws grids
d_east = 0.
d_north = 0.

# get all models into useable objects
modem_data = modem.Data()
modem_data.read_data_file(data_fn)

ws_sm2 = ws.WSModel(mfn_ws_sm2)
ws_sm3 = ws.WSModel(mfn_ws_sm2)

modem_all = modem.Model()
modem_all.read_model_file(mfn_all_sm500)

modem_tip = modem.Model()
modem_tip.read_model_file(mfn_tipper)

#--> interpolate on to the base model 
# smooth over the ws models because their resistivities are so low and
# the models are coarse. 
nr_ws_sm2 = interp_grid(ws_sm2, modem_all, shift_east=d_east, 
                        shift_north=d_north, smooth_kernel=None, pad=5)
                        
nr_ws_sm3 = interp_grid(ws_sm3, modem_all, shift_east=d_east, 
                        shift_north=d_north, smooth_kernel=None, pad=5)
                        
nr_tip = interp_grid(modem_tip, modem_all, pad=2)

#--> average all as a geometric mean
#avg_res = (nr_ws_sm2*nr_ws_sm3*modem_all.res_model*nr_tip)**(1./4)
avg_res = (nr_ws_sm2*nr_tip*modem_all.res_model)**(1./3)

x, y = np.meshgrid(modem_all.grid_east, modem_all.grid_north)
kk = 15
kwargs = {'cmap':'jet_r', 'vmin':0, 'vmax':4}

fig = plt.figure(4)
ax1 = fig.add_subplot(2,3,1, aspect='equal')
ax1.pcolormesh(x, y, np.log10(modem_all.res_model[:, :, kk]), **kwargs)

ax2 = fig.add_subplot(2,3,2, aspect='equal', sharex=ax1, sharey=ax1)
ax2.pcolormesh(x, y, np.log10(nr_tip[:, :, kk]), **kwargs)

ax3 = fig.add_subplot(2,3,3, aspect='equal', sharex=ax1, sharey=ax1)
ax3.pcolormesh(x, y, np.log10(nr_ws_sm2[:, :, kk]), **kwargs)

ax4 = fig.add_subplot(2,3,4, aspect='equal', sharex=ax1, sharey=ax1)
ax4.pcolormesh(x, y, np.log10(nr_ws_sm3[:, :, kk]), **kwargs)

ax5 = fig.add_subplot(2,3,5, aspect='equal', sharex=ax1, sharey=ax1)
ax5.pcolormesh(x, y, np.log10(avg_res[:, :, kk]), **kwargs)


for ax in [ax1, ax2, ax3, ax4, ax5]:
    ax.scatter(modem_data.data_array['rel_east'], 
                modem_data.data_array['rel_north'], 
                marker='v', c='k')
    ax.axis('tight')
    
plt.show()
modem_all.res_model = avg_res.copy()
modem_all.write_model_file(save_path=r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions",
                            model_fn_basename='mshn_avg_all_v3.rho')