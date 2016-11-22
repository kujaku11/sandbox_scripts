# -*- coding: utf-8 -*-
"""
Created on Fri Oct 07 12:25:44 2016

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# calibration from .cac file
cac_cal_fn = r"D:\Peacock\MTData\Ant_calibrations\ant_2334.csv"
cac_cal_fn_2264 = r"D:\Peacock\MTData\Ant_calibrations\ant_2264.csv"

# antamt.cal
ant_fn = r"d:\Peacock\MTData\Ant_calibrations\amtant.cal"

with open(ant_fn, 'r') as fid:
    lines = fid.readlines()
    
ant_dict = {}
for line in lines:
    if 'amt' in line.lower():
        freq = float(line.strip().split()[-1])*np.pi*2
    elif '1.00000' in line or line.strip() == '':
        continue
    else:
        line_list = line.strip().split()
        coil_key = line_list[0].strip()
        amp_01 = float(line_list[1])
        phase_01 = float(line_list[2])/1000
        amp_02 = float(line_list[3])
        phase_02 = float(line_list[4])
        try:
            ant_dict[coil_key][freq] = (amp_01, phase_01, amp_02, amp_01)
        except KeyError:
            ant_dict[coil_key] = {}
            ant_dict[coil_key][freq] = (amp_01, phase_01, amp_02, amp_01)

# write new calibration files for birrp
for ant_key in ant_dict.keys():
    ant_fn_coil = os.path.join(os.path.dirname(ant_fn), 'ant_{0}.csv'.format(ant_key))
    ant_arr = np.zeros((len(ant_dict[ant_key].keys()), 3))

    for ii, f_key in enumerate(sorted(ant_dict[ant_key].keys())):
        ant_arr[ii][0] = f_key
        amp = ant_dict[ant_key][f_key][0]
        phase = ant_dict[ant_key][f_key][1]
        
        re = np.sqrt(amp**2/(1+np.tan(phase)**2))
        im = re*np.tan(phase)
        
        # I'm not sure why you need a factor of sqrt(10) but that seems to 
        # make the amplitudes line up with what is out put by zonge codes
        ant_arr[ii][1] = re/10
        ant_arr[ii][2] = im/10
        
    # need to get response inot real and imaginary parts for birrp
    np.savetxt(ant_fn_coil, ant_arr, delimiter=',', fmt='%.4e')










            
#cac_arr = np.loadtxt(cac_cal_fn, 
#                     delimiter=',',
#                     skiprows=1,
#                     dtype={'names':('frequency', 'amplitude', 'phase'),
#                            'formats':(np.float, np.float, np.float)})
#cac_arr_2264 = np.loadtxt(cac_cal_fn_2264, 
#                     delimiter=',',
#                     skiprows=1,
#                     dtype={'names':('frequency', 'amplitude', 'phase'),
#                            'formats':(np.float, np.float, np.float)})




                            
#fig = plt.figure(1)
#ax_amp = fig.add_subplot(2, 1, 1)
#ax_phase = fig.add_subplot(2, 1, 2, sharex=ax_amp)
#
#ax_amp.loglog(cac_arr['frequency'], cac_arr['amplitude'], marker='o', color='b')
#ax_amp.loglog(cac_arr_2264['frequency'], cac_arr['amplitude'], marker='^', color=(0, 0, .75))
#ax_amp.loglog(ant_arr[:, 0], ant_arr[:, 1], marker='*', color='g')
#ax_amp.loglog(ant_arr[:, 0], ant_arr[:, 3], marker='v', color='r')
#
#ax_amp.set_xlabel('Frequency (Hz)')
#ax_amp.set_ylabel('Amplitude')
#
#ax_phase.semilogx(cac_arr['frequency'], 
#                  np.unwrap(np.rad2deg(cac_arr['phase']/1000)), 
#                  marker='o', color='b')
#ax_phase.semilogx(cac_arr_2264['frequency'],
#                  np.unwrap(np.rad2deg(cac_arr_2264['phase']/1000)), 
#                  marker='^', color=(0, 0, .75))
#ax_phase.semilogx(ant_arr[:, 0], 
#                  np.unwrap(np.rad2deg(ant_arr[:, 2]/1000)),
#                  marker='*', color='g')
#ax_phase.semilogx(ant_arr[:, 0], 
#                  np.unwrap(np.rad2deg(ant_arr[:, 4])),
#                  marker='v', color='r')
#
#ax_phase.set_xlabel('Frequency (Hz)')
#ax_phase.set_ylabel('Phase')
#
#plt.tight_layout()
#plt.show()


