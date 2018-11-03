# -*- coding: utf-8 -*-
"""
Plot changes in rms between models

Created on Fri Nov  2 14:24:01 2018

@author: jpeacock
"""

import matplotlib.pyplot as plt
import mtpy.modeling.modem as modem
import numpy as np
from matplotlib.ticker import MultipleLocator

res_fn_01 = r"c:\Users\jpeacock\Documents\ShanesBugs\TorC_2018\modem_inv\inv_03\tc_z03_t02_c02_NLCG_097.res"
res_fn_02 = r"c:\Users\jpeacock\Documents\ShanesBugs\TorC_2018\modem_inv\inv_03\tc_test_no_conductor.res"
station_list = ['TC{0:03}'.format(ii) for ii in [20, 27, 28, 29, 30, 31, 32]]
ns = len(station_list)
fs = 12


r1 = modem.Residual()
r1.read_residual_file(res_fn_01)

r2 = modem.Residual()
r2.read_residual_file(res_fn_02)

delta_rms = np.abs(r2.residual_array['z'])/r2.residual_array['z_err'] - \
            np.abs(r1.residual_array['z'])/r1.residual_array['z_err']

fig = plt.figure(1)
fig.clf()

ax1 = fig.add_subplot(1, 1, 1)

legend_list = []
for ii, station in enumerate(station_list):
    c = float(ii)/ns
    station_find = np.where(r1.residual_array['station'] == station)[0][0]
    line_color = (c, 1-c, 1-c)
    l1, = ax1.semilogx(r1.period, 
                       np.round(delta_rms[station_find].mean(axis=(1,2)), decimals=3),
                       color=line_color)
    legend_list.append(l1)
    
ax1.legend(legend_list, station_list, loc='upper left')
ax1.set_xlabel('period (s)', fontdict={'size':fs, 'weight':'bold'})
ax1.set_ylabel('$\Delta$ RMS', fontdict={'size':fs, 'weight':'bold'})
ax1.grid(which='both', color=(.5, .5, .5), ls='--')
ax1.set_axisbelow(True)

plt.show()

fig_02 = plt.figure(2)
fig_02.clf()

ax2 = fig_02.add_subplot(1, 1, 1, aspect='equal')

m_list = []
m_label = []
for ii, station in enumerate(station_list):

    station_find = np.where(r1.residual_array['station'] == station)[0][0]
    
    s_rms = np.nanmean(delta_rms[station_find][11:]) 
    print('{0} - {1:.2f}'.format(station, s_rms))
    c = s_rms/1.4
    if c < 0:
        line_color = (1-abs(c), 1, 1)
        print line_color
    else:
        line_color = (1, 1-c, 1-c)
    m1 = ax2.scatter(r1.residual_array[station_find]['lon'],
                 r1.residual_array[station_find]['lat'],
                 marker='o',
                 s=105,
                 c=line_color)
#        m1, = ax2.plot([None, None], color=line_color)
    
    m_list.append(m1)
    m_label.append('{0}  {1:.2f}'.format(station, s_rms))
    ax2.text(r1.residual_array[station_find]['lon'],
             r1.residual_array[station_find]['lat']+.005,
             '{0}'.format(station),
             horizontalalignment='center',
             verticalalignment='top')

ax2.legend(m_list, m_label, loc='upper left')
ax2.set_xlabel('longitude (deg)', fontdict={'size':fs, 'weight':'bold'})
ax2.set_ylabel('latitude (deg)', fontdict={'size':fs, 'weight':'bold'})
ax2.grid(which='both', color=(.5, .5, .5), ls='--')
ax2.set_axisbelow(True)
ax2.xaxis.set_major_locator(MultipleLocator(.025))
ax2.yaxis.set_major_locator(MultipleLocator(.025))

ax2.set_xlim((-107.225, -107.325))
ax2.set_ylim((33.10, 33.25))

fig.savefig(r"c:\Users\jpeacock\Documents\ShanesBugs\TorC_2018\rms_conductor_test.png",
               dpi=600)
fig_02.savefig(r"c:\Users\jpeacock\Documents\ShanesBugs\TorC_2018\rms_map_conductor_test.png",
               dpi=600)

plt.show()



