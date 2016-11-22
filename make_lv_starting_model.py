# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 12:26:05 2014

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sps

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

mfn_no_tipper = r"/home/jpeacock/Documents/ModEM/LV/Inv1_dp_no_tipper/lv_no_tipper_NLCG_100.rho"
mfn_tipper = r"/home/jpeacock/Documents/ModEM/LV/NAS/hs_tipper/lv_tipper_NLCG_029.rho"

m_obj_t = modem.Model()
m_obj_t.read_model_file(mfn_tipper)

m_obj_nt = modem.Model()
m_obj_nt.read_model_file(mfn_no_tipper)

new_res = np.sqrt(m_obj_t.res_model*m_obj_nt.res_model)

#new_res = 10**((.7*np.log10(m_obj_t.res_model)+.3*np.log10(m_obj_nt.res_model)))
#new_res = .5*(m_obj_t.res_model+m_obj_nt.res_model)

## make a base model that is 1000 ohm-m
#new_res = m_obj_t.res_model.copy()
#
## then anywhere either model is less than 100 ohm-m set it to base model
##index_t = np.where(m_obj_t.res_model < 100)
##new_res[index_t] = m_obj_t.res_model[index_t]
#
#index_nt = np.where(m_obj_nt.res_model < 20)
#new_res[index_nt] = m_obj_nt.res_model[index_nt]

#for ii in range(m_obj_t.grid_z.shape[0]):
#    new_res[:, :, ii] = 10**smooth_2d(np.log10(new_res[:, :, ii]), 7)


#--> plot to see how we did
grid_east, grid_north = np.meshgrid(m_obj_t.grid_east, m_obj_t.grid_north)

fig = plt.figure(5)
plt.clf()
                 
co_mb = fig.add_subplot(1, 3, 1, aspect='equal')
co_mb.pcolormesh(grid_east, grid_north, np.log10(m_obj_t.res_model[:, :, 30]), 
                 cmap='jet_r',
                 vmin=-1, 
                 vmax=4)
                 
co_mb = fig.add_subplot(1, 3, 2, aspect='equal')
co_mb.pcolormesh(grid_east, grid_north, np.log10(m_obj_nt.res_model[:, :, 30]), 
                 cmap='jet_r',
                 vmin=-1, 
                 vmax=4)
                 
co_mb = fig.add_subplot(1, 3, 3, aspect='equal')
co_mb.pcolormesh(grid_east, grid_north, np.log10(new_res[:, :, 30]), 
                 cmap='jet_r',
                 vmin=-1, 
                 vmax=4)
#co_mb.pcolormesh(grid_east, grid_north, smooth_2d(np.log10(new_res[:, :, 33]), 11), 
#                 cmap='jet_r',
#                 vmin=-1, 
#                 vmax=4)
plt.show()

m_obj_nt.res_model = new_res.copy()
m_obj_nt.write_model_file(save_path=r"/home/jpeacock/Documents/ModEM/LV",
                          model_fn_basename=r"lv_sm_avg.rho")