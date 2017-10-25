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

import matplotlib.pyplot as plt


dir_path_01 = r"c:\Users\jrpeacock\Documents\Test_Data\Tongario\original"
dir_path_02 = r"c:\Users\jrpeacock\Documents\Test_Data\Tongario\repeat"

station_num = [3, 4, 13, 24, 30, 70, 62, 1, 2, 4, 8, 9, 12, 14, 27, 28, 25]
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
    
fig = plt.figure(1)
fig.subplots_adjust(left=.06, bottom=.06, right=.98, top=.95)
line_list = []
label_list = []
for ii, r_arr in enumerate(rpt_arr[0:16]):
    ax = fig.add_subplot(16, 1, ii+1)
    line = ax.fill_between(1./rpt_arr['frequency'][0], 
                       np.zeros(40),
                       signal.medfilt(np.mean(rpt_arr['phimax'][noiseless],
                                              axis=0),
                                      kernel_size=7),
                        color=(.75, .75, .75),
                        alpha=.35)

    line = ax.errorbar(1./r_arr['frequency'], 
                        signal.medfilt(r_arr['phimax'], kernel_size=7),
                        yerr=signal.medfilt(r_arr['phimax_err'], kernel_size=7),
                        capsize=5,
                        capthick=.5)
    
    line_list.append(line)
    label_list.append(r_arr['station'])
    ax.set_xscale('log')
    ax.grid(which='both', color=(.5, .5, .5), ls='--')
    ax.set_axisbelow(True)
    ax.set_ylim(0, 90)
    ax.set_yticks(np.arange(0, 90, 10))
    ax.set_ylabel('Phimax', fontdict={'size':12, 'weight':'bold'})
    ax.legend(line, [r_arr['station']], loc='upper left')

#line_list.append(line)
#label_list.append('Error')
    
#fig.legend(line_list, label_list, loc='upper center', ncol=6)

ax.set_xlabel('Period (s)', fontdict={'size':12, 'weight':'bold'})


plt.show()