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
import mtpy.modeling.ws3dinv as ws

data_fn = r'/home/jpeacock/Documents/ModEM/LV/sm_comb_inv2/lv_dp_err7.dat'

modem_model_fn = r"/home/jpeacock/Documents/ModEM/LV/sm_comb_inv2/ModEM_Model_rw.ws"
ws_init_fn = r"/home/jpeacock/Documents/wsinv3d/LV/Inv_lv_coarse_2/WSInitialModel"
ws_data_fn = r"/home/jpeacock/Documents/wsinv3d/LV/Inv_lv_coarse_2/WS_data_lv_coarse_2_4_small.dat"
ws_station_fn = r"/home/jpeacock/Documents/wsinv3d/LV/Inv_lv_coarse_2/WS_Station_Locations.txt"

#difference between modem and ws grids
shift_east = -7000.
shift_north = 500.

modem_data = modem.Data()
modem_data.read_data_file(data_fn)

modem_mod = modem.Model()
modem_mod.read_model_file(modem_model_fn)


ws_mesh = ws.WSMesh()
ws_mesh.read_initial_file(ws_init_fn)

ws_data = ws.WSData()
ws_data.read_data_file(data_fn=ws_data_fn, station_fn=ws_station_fn)


print 'Start Time = {0}'.format(time.ctime())

pad = 1
north, east = np.broadcast_arrays(modem_mod.grid_north[:, None], 
                                  modem_mod.grid_east[None, :])
                                  
#2) do a 2D interpolation for each layer, much faster
new_res = np.zeros((ws_mesh.grid_north.shape[0],
                    ws_mesh.grid_east.shape[0],
                    ws_mesh.grid_z.shape[0]))
                    
for zz in range(ws_mesh.grid_z.shape[0]):
    try:
        old_zz = np.where(modem_mod.grid_z >= ws_mesh.grid_z[zz])[0][0]
    except IndexError:
        old_zz = -1
                      
    print 'New depth={0:.2f}; old depth={1:.2f}'.format(ws_mesh.grid_z[zz],
                                                        modem_mod.grid_z[old_zz])
                      
    new_res[:, :, zz] = spi.griddata((north.ravel(), east.ravel()),
                                     modem_mod.res_model[:, :, old_zz].ravel(),
                                     (ws_mesh.grid_north[:, None]+shift_north, 
                                      ws_mesh.grid_east[None, :]+shift_east),
                                     method='linear')
                                     
    new_res[0:pad, pad:-pad, zz] = new_res[pad, pad:-pad, zz]    
    new_res[-pad:, pad:-pad, zz] = new_res[-pad-1, pad:-pad, zz]
    new_res[:, 0:pad, zz] = new_res[:, pad, zz].repeat(pad).reshape(
                                              new_res[:, 0:pad, zz].shape)    
    new_res[:, -pad:, zz] = new_res[:, -pad-1, zz].repeat(pad).reshape(
                                              new_res[:, -pad:, zz].shape)
                                        
                         

#
new_res[np.where(np.nan_to_num(new_res)==0.0)] = 100.0
ws_mesh.write_initial_file(initial_fn=r"/home/jpeacock/Documents/wsinv3d/LV/ws_sm_modem_lv", 
                           res_model=new_res, res_list=None)
                           
omfid = file(ws_mesh.initial_fn, 'r')
mlines = omfid.readlines()
omfid.close()

mfid = file(ws_mesh.initial_fn, 'w')
mfid.writelines(mlines[0:26])
for kk in range(ws_mesh.grid_z.shape[0]):
    for jj in range(ws_mesh.grid_east.shape[0]):
        for ii in range(ws_mesh.grid_north.shape[0]):
            res_num = new_res[(ws_mesh.grid_north.shape[0]-1)-ii, jj, kk] 
            mfid.write('{0:12.5e}\n'.format(res_num))
mfid.close()

x, y = np.meshgrid(ws_mesh.grid_east, ws_mesh.grid_north)
fig = plt.figure(2)
ax1 = fig.add_subplot(1,2,1, aspect='equal')
ax1.pcolormesh(x, y, np.log10(new_res[:, :, 25]), cmap='jet_r', vmin=-1, vmax=4)
ax1.scatter(ws_data.data['east'], ws_data.data['north'], marker='v', c='k')

ax2 = fig.add_subplot(1, 2, 2, aspect='equal')
mx, my = np.meshgrid(modem_mod.grid_east, modem_mod.grid_north)
ax2.pcolormesh(mx, my, np.log10(modem_mod.res_model[:, :, 27]),
               cmap='jet_r', vmin=-1, vmax=4)
ax2.scatter(modem_data.data_array['rel_east'], modem_data.data_array['rel_north'],
            marker='v', c='k')
            
for ax in [ax1, ax2]:
    ax.set_ylim(-20000, 20000)
    ax.set_xlim(-20000, 20000)
plt.show()


print 'End Time = {0}'.format(time.ctime())


