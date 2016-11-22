# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 14:42:53 2014

@author: jpeacock-pr
"""


import mtpy.modeling.modem_new as modem
import scipy.interpolate as spi
import numpy as np
import time
import matplotlib.pyplot as plt
#
data_fn = r'/home/jpeacock/Documents/ModEM/LV/sm_avg_inv1/lv_dp_23p_err07_tip1.dat'

#data_fn = r'/home/jpeacock/Documents/ModEM/MB_MT/WS_StartingModel_03_tipper/mb_data_tipper.dat'

#data_fn = r'/home/jpeacock/Documents/ModEM/MB_MT/WS_StartingModel_03_tipper/mb_data_tipper.dat'

new_model_fn = r'/home/jpeacock/Documents/ModEM/LV/sm_avg_inv1/lv_avg_err07_NLCG_018.rho'
old_model_fn = r"/home/jpeacock/Documents/ModEM/MB_MT/WS_StartingModel_03_tipper/cov3_mb_tipper_NLCG_028.rho"

interpolation_dim = '2d'

new_mod = modem.Model()
new_mod.read_model_file(new_model_fn)
new_mod.res_model[:, :, :] = 1000

old_mod = modem.Model()
old_mod.read_model_file(old_model_fn)
#old_mod.res_model[np.where(old_mod.res_model) < 1.0] = 1.0

data_obj = modem.Data()
data_obj.read_data_file(data_fn)

new_mod.station_locations = data_obj.station_locations.copy()

#caluclate an offset between grids.
diff_east = old_mod.grid_east[16]-new_mod.grid_east[20]
diff_north = old_mod.grid_north[16]-new_mod.grid_north[20]
#diff_east = 0
#diff_north = 0
pad = 5

  

print 'Start Time = {0}'.format(time.ctime())

if interpolation_dim == '2d':
    north, east = np.broadcast_arrays(old_mod.grid_north[:, None]+diff_north, 
                                      old_mod.grid_east[None, :]-diff_east)
                                      
    #2) do a 2D interpolation for each layer, much faster
    new_res = np.zeros((new_mod.grid_north.shape[0],
                        new_mod.grid_east.shape[0],
                        new_mod.grid_z.shape[0]))
                        
    for zz in range(new_mod.grid_z.shape[0]):
        try:
            old_zz = np.where(old_mod.grid_z >= new_mod.grid_z[zz])[0][0]
        except IndexError:
            old_zz = -1
                          
        print 'New depth={0:.2f}; old depth={1:.2f}'.format(new_mod.grid_z[zz],
                                                            old_mod.grid_z[old_zz])
                          
        new_res[:, :, zz] = spi.griddata((north.ravel(), east.ravel()),
                                         old_mod.res_model[:, :, old_zz].ravel(),
                                         (new_mod.grid_north[:, None], 
                                          new_mod.grid_east[None, :]),
                                         method='linear')
                                         
        new_res[:, :, zz] = spi.griddata((north.ravel(), east.ravel()),
                                         old_mod.res_model[:, :, old_zz].ravel(),
                                         (new_mod.grid_north[:, None], 
                                          new_mod.grid_east[None, :]),
                                         method='linear')
                                         
        new_res[0:pad, pad:-pad, zz] = new_res[pad, pad:-pad, zz]    
        new_res[-pad:, pad:-pad, zz] = new_res[-pad-1, pad:-pad, zz]
        new_res[:, 0:pad, zz] = new_res[:, pad, zz].repeat(pad).reshape(
                                                  new_res[:, 0:pad, zz].shape)    
        new_res[:, -pad:, zz] = new_res[:, -pad-1, zz].repeat(pad).reshape(
                                                  new_res[:, -pad:, zz].shape)
                                        
elif interpolation_dim == '3d':
    #1) first need to make x, y, z have dimensions (nx, ny, nz), similar to res
    north, east, vert = np.broadcast_arrays(old_mod.grid_north[:, None, None]+diff_north, 
                                            old_mod.grid_east[None, :, None]-diff_east, 
                                            old_mod.grid_z[None, None, :])

    #2) next interpolate ont the new mesh (3D interpolation, slow)
    new_res = spi.griddata((north.ravel(), east.ravel(), vert.ravel()),
                            old_mod.res_model.ravel(),
                            (new_mod.grid_north[:, None, None], 
                             new_mod.grid_east[None, :, None], 
                             new_mod.grid_z[None, None, :]),
                             method='linear')
                         

#
new_res[np.where(np.nan_to_num(new_res)==0.0)] = 1000.0


for zz in range(new_mod.grid_z.shape[0]):
    new_res[0:pad+1, :, zz] = new_res[pad+1, :, zz]

new_mod.res_model = new_res

#new_mod.write_model_file(save_path=r"/home/jpeacock/Documents/ModEM/MB_MT/WS_StartingModel_03_tipper",
#                     model_fn_basename='WS_sm_cov3_fine_grid.rho')
new_mod.write_model_file(save_path=r"/home/jpeacock/Documents/ModEM/LV",
                     model_fn_basename='lv_mb_sm.rho')


x, y = np.meshgrid(new_mod.grid_east, new_mod.grid_north)
fig = plt.figure(2)
ax1 = fig.add_subplot(1,1,1, aspect='equal')

ax1.pcolormesh(x, y, np.log10(new_res[:, :, 30]), cmap='jet_r', vmin=-1, vmax=4)
ax1.scatter(data_obj.station_locations['rel_east'], 
            data_obj.station_locations['rel_north'],
            marker='v', c='k')
plt.show()


print 'End Time = {0}'.format(time.ctime())


