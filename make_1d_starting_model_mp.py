# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 14:38:14 2018

@author: jpeacock
"""

import os
import numpy as np
#from scipy import signal
#import matplotlib.pyplot as plt
from mtpy.core import z as mtz
from mtpy.modeling import modem
from mtpy.modeling import occam1d
from scipy.interpolate import griddata
import pickle

dfn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_08\mp_modem_data_z05.dat"
mfn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_08\mp_sm02_topo.rho"
occam1d_path = r"c:\MinGW32-xy\Peacock\occam\occam1d.exe"
sv_dir = os.path.dirname(dfn)
# =============================================================================
# read in data file and get mean and median of determinant
# =============================================================================
d_obj = modem.Data()
d_obj.read_data_file(dfn)

m_obj = modem.Model()
m_obj.read_model_file(mfn)

ocm = occam1d.Model()
ocm.write_model_file(save_path=sv_dir, model_depth=m_obj.grid_z)

res_arr = np.zeros((d_obj.data_array.shape[0],
                    m_obj.res_model.shape[-1]))

x = np.zeros(d_obj.data_array.shape[0])
y = np.zeros(d_obj.data_array.shape[0])
for ii, d_arr in enumerate(d_obj.data_array):
    x[ii] = d_arr['rel_north']
    y[ii] = d_arr['rel_east']
    z_obj = mtz.Z(d_arr['z'], freq=1./d_obj.period_list)
    
    d_index = np.where(m_obj.grid_z > d_arr['rel_elev'])[0][0]
    
    # make occam data file
    ocd = occam1d.Data()
    rp_tuple = (1./d_obj.period_list,
                z_obj.res_det, z_obj.res_det_err,
                z_obj.phase_det, z_obj.phase_det_err)
    ocd.save_path = sv_dir
    ocd.write_data_file(rp_tuple=rp_tuple,
                       mode='det',
                       res_err=5,
                       phase_err=2.5)
    ### make startup file
    ocs = occam1d.Startup()
    ocs.start_rho = z_obj.res_det.mean()
    ocs.data_fn = ocd.data_fn
    ocs.model_fn = ocm.model_fn
    ocs.save_path = sv_dir
    ocs.max_iter = 10
    ocs.write_startup_file()
    
    occam1d.Run(ocs.startup_fn, occam_path=occam1d_path, mode='Det')
    try:
        m_ocm = occam1d.Model()
        m_ocm.read_iter_file(os.path.join(sv_dir, 'Det_5.iter'), 
                             ocm.model_fn)
        res_arr[ii, d_index:] = m_ocm.model_res[1:-(d_index+2), 1]
    except:
        print('Occam did not run for {0}'.format(d_arr['station']))

# =============================================================================
# make occam 1d model from model file
# =============================================================================
points = np.array([x, y])

grid_x, grid_y = np.meshgrid(m_obj.grid_north, m_obj.grid_east)

res_1d = griddata(points, res_arr[40], (grid_x, grid_y), method='cubic')


#res_1d = np.zeros_like(m_obj.res_model)
#res_1d[:, :, :] = 10**signal.medfilt(m_ocm.model_res[3:, 1], kernel_size=7) 
#res_1d[np.where(m_obj.res_model > 1E10)] = 1E12
#
#m_obj.res_model = res_1d
#m_obj.write_model_file(model_fn_basename='mp_sm1d_topo.rho')
#m_obj.write_vtk_file(vtk_fn_basename='mp_sm1d_topo')

#fig = plt.figure()
#
#ax = fig.add_subplot(1, 1, 1)
#l1, = ax.loglog(d_obj.period_list, mean_rho, lw=2, color=(.75, .25, 0))
#l2, = ax.loglog(d_obj.period_list, median_rho, lw=2, color=(0, .25, .75))
#
#ax.loglog(d_obj.period_list, np.repeat(mean_rho.mean(),
#                                       d_obj.period_list.size),
#          ls='--', lw=2, color=(.75, .25, 0))
#ax.loglog(d_obj.period_list, np.repeat(np.median(median_rho), 
#                                       d_obj.period_list.size),
#          ls='--', lw=2, color=(0, .25, .75))
#
#ax.set_xlabel('Period (s)', fontdict={'size':12, 'weight':'bold'})
#ax.set_ylabel('Resistivity (Ohm-m)', fontdict={'size':12, 'weight':'bold'})
#
#ax.legend([l1, l2], ['Mean = {0:.1f}'.format(mean_rho.mean()),
#                     'Median = {0:.1f}'.format(np.median(median_rho))],
#          loc='upper left')
#ax.grid(which='both', ls='--', color=(.75, .75, .75))
#
#plt.show()
