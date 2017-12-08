# -*- coding: utf-8 -*-
"""
Created on Fri Oct 06 12:51:50 2017

@author: jrpeacock
"""

import os
import mtpy.core.mt as mt
import numpy as np
import mtpy.analysis.pt as mtpt
import scipy.signal as signal
import scipy.interpolate as interpolate

import matplotlib.pyplot as plt


dir_path_01 = r"c:\Users\jrpeacock\Documents\Test_Data\Tongario\original"
dir_path_02 = r"c:\Users\jrpeacock\Documents\Test_Data\Tongario\repeat"

station_num = [3, 4, 13, 24, 30, 70, 62, 1, 2, 4, 8, 9, 12, 14, 27, 28, 25]
plot_station_index = [0, 3, 4, 5, 6]
noiseless = np.array([0, 3, 5, 6, 8, 10, 11, 13, 14, 15])
rpt_arr = np.zeros(len(station_num),
                   dtype=[('station', 'S10'),
                             ('frequency', (np.float, (40,))),
                             ('phimax', (np.float, (40))),
                             ('phimin', (np.float, (40,))),
                             ('phimax_err', (np.float, (40,))),
                             ('phimin_err', (np.float, (40,)))])

z_err = np.zeros((40, 2, 2), dtype=np.complex)

for ii, station in enumerate(station_num):
    fn_01 = os.path.join(dir_path_01, 'TNG-0{0:02}.edi'.format(station))
    fn_02 = os.path.join(dir_path_02, 'TNG-3{0:02}.edi'.format(station))
    
    mt_01 = mt.MT()
    mt_01.read_mt_file(fn_01)
    
    mt_02 = mt.MT()
    mt_02.read_mt_file(fn_02)
    
    z_err += mt_01.Z.z_err
    z_err += mt_02.Z.z_err
    
    rpt = mtpt.ResidualPhaseTensor(mt_01.pt, mt_02.pt)
    rpt_arr['frequency'][ii] = mt_01.Z.freq
    rpt_arr['station'][ii] = mt_01.station
    rpt_arr['phimax'][ii][:] = rpt.residual_pt.phimax
    rpt_arr['phimin'][ii][:] = rpt.residual_pt.phimin
    rpt_arr['phimax_err'][ii][:] = rpt.residual_pt.phimax_err
    rpt_arr['phimin_err'][ii][:] = rpt.residual_pt.phimin_err
    
## make an error phase tensor
#z_err_object = mt.MTz.Z(z_array=z_err/10., freq=rpt_arr['frequency'][0])
#err_pt = mtpt.PhaseTensor(z_object=z_err_object)
    
fig = plt.figure(1, [7, 8])
fig.subplots_adjust(left=.1, bottom=.06, right=.98, top=.95, hspace=.07)
line_list = []
label_list = []
plot_period = 1./rpt_arr['frequency'][0]
interp_period = np.arange(plot_period.min(), plot_period.max())

noise = signal.medfilt(np.mean(rpt_arr['phimax'][noiseless], axis=0),
                           kernel_size=7)
noise_func = interpolate.interp1d(plot_period, noise, kind='slinear')
plot_noise = noise_func(interp_period)

for ii, r_arr in enumerate(rpt_arr[plot_station_index]):
    phimax = signal.medfilt(r_arr['phimax'], kernel_size=7)
    phimax_err = signal.medfilt(r_arr['phimax_err'], kernel_size=7)
    
    pm_func = interpolate.interp1d(plot_period, phimax, kind='slinear')
    pm_err_func = interpolate.interp1d(plot_period, phimax_err, kind='slinear')
    
    ax = fig.add_subplot(len(plot_station_index), 1, ii+1)
    line1 = ax.fill_between(interp_period, 
                           np.zeros(len(interp_period)),
                           plot_noise,
                           color=(.65, .65, .65),
                           alpha=.35)

    line2 = ax.errorbar(plot_period, 
                       pm_func(plot_period),
                       pm_err_func(plot_period),
                       ls='None',
                       capsize=8,
                       capthick=1.5, 
                       lw=1.5,
                       color=u'#1f77b4')
    line3 = ax.errorbar(interp_period, 
                       pm_func(interp_period),
                       yerr=None,
                       capsize=8,
                       capthick=1.5, 
                       lw=1.5,
                       color=u'#1f77b4')
    
    line_list.append(line3)
    label_list.append(r_arr['station'])
    ax.set_xscale('log')
    if ii < 4:
        ax.xaxis.set_tick_params(labelbottom='off')
    ax.set_xlim(plot_period.min(), plot_period.max())
    ax.grid(which='both', color=(.75, .75, .75), ls='--', alpha=.7)
    
    ax.set_axisbelow(True)
    ax.set_ylim(0, 90)
    ax.set_yticks(np.arange(0, 90, 10))
    ax.set_ylabel('Phimax (deg)', fontdict={'size':12, 'weight':'bold'})
    ax.legend(line3, [r_arr['station']], loc='upper left')
    

#line_list.append(line)
#label_list.append('Error')
    
#fig.legend(line_list, label_list, loc='upper center', ncol=6)

ax.set_xlabel('Period (s)', fontdict={'size':12, 'weight':'bold'})

#fig.savefig(r"c:\Users\jrpeacock\Documents\Test_Data\Tongario\Tongario_phimax_comparison_vs_error_final.pdf",
#            dpi=600)

plt.show()