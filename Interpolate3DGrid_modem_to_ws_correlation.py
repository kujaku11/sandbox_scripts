# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 14:42:53 2014

@author: jpeacock-pr
"""


import mtpy.modeling.modem_new as modem
import scipy.interpolate as spi
import scipy.signal as sps
import numpy as np
import time
import matplotlib.pyplot as plt
import mtpy.modeling.ws3dinv as ws

data_fn = r'/home/jpeacock/Documents/ModEM/LV/sm_comb_inv2/lv_dp_err7.dat'

modem_model_fn = r"/home/jpeacock/Documents/ModEM/LV/sm_comb_inv3/lv_comb_NLCG_084.rho"
ws_init_fn = r"/home/jpeacock/Documents/wsinv3d/LV/sm_modem_inv1/WSInitialMesh"
ws_data_fn = r"/home/jpeacock/Documents/wsinv3d/LV/sm_modem_inv1/WS_data_sm_modem_inv1_8_small.dat"
ws_station_fn = r"/home/jpeacock/Documents/wsinv3d/LV/WS_Station_Locations.txt"
ws_model_fn = r"/home/jpeacock/Documents/wsinv3d/LV/sm_modem_inv2/lv_sm_modem_inv2_fine_model.05"

#difference between modem and ws grids
shift_east = -7000.
shift_north = 500.

# --> ModEM
# read in modem data file
modem_data = modem.Data()
modem_data.read_data_file(data_fn)

# read in modem model file
modem_model = modem.Model()
modem_model.read_model_file(modem_model_fn)

#--> WSINV3D
# read in initial mesh file
ws_mesh = ws.WSMesh()
ws_mesh.read_initial_file(ws_init_fn)

#read in data file
ws_data = ws.WSData()
ws_data.read_data_file(data_fn=ws_data_fn, station_fn=ws_station_fn)

# read in model file
ws_model = ws.WSModel(ws_model_fn)

# we need to get WS and ModEM on the same modeling grid.  Choose the ModEM grid
pad = 2   # number of padding cells within the modeling grid to change values

# make north and east arrays for WS, similar to meshgrid
ws_north, ws_east = np.broadcast_arrays(ws_model.grid_north[:, None], 
                                        ws_model.grid_east[None, :])
                                  
# make a new resistivity array that will be filled by interpolation
new_res = np.zeros((modem_model.grid_north.shape[0],
                    modem_model.grid_east.shape[0],
                    modem_model.grid_z.shape[0]))




#2) do a 2D interpolation for each layer, much faster                    
for zz in range(modem_model.grid_z.shape[0]):
    try:
        old_zz = np.where(ws_model.grid_z >= modem_model.grid_z[zz])[0][0]
    except IndexError:
        old_zz = -1
                      
    print 'New depth={0:.2f}; old depth={1:.2f}'.format(modem_model.grid_z[zz],
                                                        ws_model.grid_z[old_zz])
    
    # interpolate ws onto modem grid in 2D for each layer
    # be sure to shift the cell                  
    new_res[:, :, zz] = spi.griddata((ws_north.ravel()-shift_north, 
                                      ws_east.ravel()+shift_east),
                                     ws_model.res_model[:, :, old_zz].ravel(),
                                     (modem_model.grid_north[:, None], 
                                      modem_model.grid_east[None, :]),
                                      method='linear')
    
    # at the edges push values from the center, this way there are no
    # sharp edges near the boundaries of the grid, it goes to a 1D earth                                 
    new_res[0:pad, pad:-pad, zz] = new_res[pad, pad:-pad, zz]    
    new_res[-pad:, pad:-pad, zz] = new_res[-pad-1, pad:-pad, zz]
    new_res[:, 0:pad, zz] = new_res[:, pad, zz].repeat(pad).reshape(
                                              new_res[:, 0:pad, zz].shape)    
    new_res[:, -pad:, zz] = new_res[:, -pad-1, zz].repeat(pad).reshape(
                                              new_res[:, -pad:, zz].shape)
                                        
                         

# make sure there are no NAN in the array 
new_res[np.where(np.nan_to_num(new_res)==0.0)] = 100.0

print 'Start Time = {0}'.format(time.ctime())
#--> correlate with modem
res_avg = np.zeros_like(new_res)

## calculate normalized cross correlation
#for zz in range(modem_model.grid_z.shape[0]):
#    # normalize each layer so the outcome is a cosine angle [0, 1]
#    fx = new_res[:, :, zz].copy()
#    gx = modem_model.res_model[:, :, zz].copy()
#    
#    #correlation assumes zero mean arrays
#    fx -= fx.mean()
#    gx -= gx.mean()
#    
#    #calculate the standard deviation of the zero-mean arrays
#    std_f = fx.std()
#    std_g = gx.std()
#    
#    #need the size of the overlapping arrays
#    nf = fx.size
#
#    # compute the normalized cross-correlation for each layer
#    # use key word mode='same' to get out the same shape as put in nf    
#    res_avg[:, :, zz] = sps.correlate2d(fx, gx, mode='same')/(std_f*std_g*nf)

# calculate normalized cross correlation
for zz in range(modem_model.grid_z.shape[0]):
    fx = new_res[:, :, zz].copy()
    gx = modem_model.res_model[:, :, zz].copy()
    
#    res_avg[:, :, zz] = np.log10(fx)-np.log10(gx)
#    res_avg[:, :, zz] = (fx+gx)/2.
    res_avg[:, :, zz] = np.sqrt(fx*gx)

print 'End Time = {0}'.format(time.ctime())

modem_model.res_model = res_avg
modem_model.write_model_file(save_path=r"/home/jpeacock/Documents/ModEM/LV/sm_avg_inv1",
                             model_fn_basename='lv_sm_avg.rho')
                             
#--> see what it looks like
# normalize the cross correlation
#res_avg /= res_avg.size**2

x, y = np.meshgrid(modem_model.grid_east, modem_model.grid_north)
fig = plt.figure(3)
for ii, zz in enumerate(range(0, 40, 5), 1):
    ax = fig.add_subplot(3, 3, ii, aspect='equal')
    cp = ax.pcolormesh(x, y, np.log10(res_avg[:, :, zz]),
                  cmap='jet_r', vmin=-1, vmax=4)
                  
    sc = ax.scatter(modem_data.data_array['rel_east'], 
                    modem_data.data_array['rel_north'],
                    marker='v', c='k')
        
    ax.set_ylim(-40000, 40000)
    ax.set_xlim(-40000, 40000)
    plt.colorbar(cp)
    print ii, res_avg[:, :, zz].min(), res_avg[:, :, zz].max()
    
plt.show()





