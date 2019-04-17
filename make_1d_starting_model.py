# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 14:38:14 2018

@author: jpeacock
"""

import os
import numpy as np
from scipy import signal
#import matplotlib.pyplot as plt
from mtpy.core import z as mtz
from mtpy.modeling import modem
from mtpy.modeling import occam1d

dfn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_08\mp_modem_data_z03_t05_topo.dat"
mfn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_08\mp_sm02_topo.rho"
occam1d_path = r"c:\MinGW32-xy\Peacock\occam\occam1d.exe"
sv_dir = os.path.dirname(dfn)
# =============================================================================
# read in data file and get mean and median of determinant
# =============================================================================
d_obj = modem.Data()
d_obj.read_data_file(dfn)

rho = np.zeros((d_obj.data_array.shape[0], d_obj.period_list.shape[0]))
phase = np.zeros_like(rho)

for ii, d_arr in enumerate(d_obj.data_array):
    z_obj = mtz.Z(d_arr['z'], freq=1./d_obj.period_list)
    rho[ii, :] = z_obj.res_det
    phase[ii, :] = z_obj.phase_det
    
#mean_rho = np.apply_along_axis(lambda x: x[np.nonzero(x)].mean(), 0, rho)
median_rho = np.apply_along_axis(lambda x: np.median(x[np.nonzero(x)]), 0, rho)
median_rho[0] = 0
#mean_phase = np.apply_along_axis(lambda x: x[np.nonzero(x)].mean(), 0, phase)
median_phase = np.apply_along_axis(lambda x: np.median(x[np.nonzero(x)]), 0, phase)
median_phase[0] = 0
# make occam data file
ocd = occam1d.Data()
rp_tuple = (1./d_obj.period_list,
            median_rho, median_rho*.05,
            median_phase, median_phase*.05)
ocd.save_path = sv_dir
ocd.write_data_file(rp_tuple=rp_tuple,
                   mode='det',
                   res_err=5,
                   phase_err=2.5)

# =============================================================================
# make occam 1d model from model file
# =============================================================================
m_obj = modem.Model()
m_obj.read_model_file(mfn)

ocm = occam1d.Model()
ocm.write_model_file(save_path=sv_dir, model_depth=m_obj.grid_z)

### make startup file
ocs = occam1d.Startup()
ocs.start_rho = median_rho.mean()
ocs.data_fn = ocd.data_fn
ocs.model_fn = ocm.model_fn
ocs.save_path = sv_dir
ocs.max_iter = 10
ocs.write_startup_file()

occam1d.Run(ocs.startup_fn, occam_path=occam1d_path, mode='Det')

m_ocm = occam1d.Model()
m_ocm.read_iter_file(os.path.join(sv_dir, 'Det_5.iter'), 
                     ocm.model_fn)

res_1d = np.zeros_like(m_obj.res_model)
res_1d[:, :, :] = 10**signal.medfilt(m_ocm.model_res[3:, 1], kernel_size=7) 
res_1d[np.where(m_obj.res_model > 1E10)] = 1E12

m_obj.res_model = res_1d
m_obj.write_model_file(model_fn_basename='mp_sm1d_topo.rho')
m_obj.write_vtk_file(vtk_fn_basename='mp_sm1d_topo')

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
