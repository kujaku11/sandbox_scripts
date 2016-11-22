# -*- coding: utf-8 -*-
"""
Created on Mon Nov 02 14:20:33 2015

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

mod_rfn = r"c:\Users\jpeacock\Documents\LV\lv_geo_avg_err03_cov5_NLCG_054.dat"
mod_dfn = r"c:\Users\jpeacock\Documents\LV\lv_geo_err03_tip07.dat"

data_obj = modem.Data()
data_obj.read_data_file(mod_dfn)

s_list = data_obj.station_locations['station'] 

## plot station responses as impedance
#mpr = modem.PlotResponse(data_fn=mod_dfn, resp_fn=mod_rfn, plot_yn='n',
#                         color_mode='color')
#
#for station in s_list:
#    mpr.mtem = '.'
#    mpr.mtmm = '.'
#    mpr.cted = (.25, .25, .25)
#    mpr.ctmd = (.25, .25, .25)
#    mpr.ctem = (0, 0, 1)
#    mpr.ctmm = (1, 0, 0)
#    mpr.ms = 3
#    mpr.lw = .65
#    mpr.plot_z = False
#    
#    mpr.plot_type = [station]
#   
#    mpr.plot()
#    mpr.redraw_plot()     
#    mpr.save_figure(r"c:\Users\jpeacock\Google Drive\LV_Geothermal\figures\Supp_{0}_modem_resp_res.pdf".format(station),
#                    fig_dpi=300)

#p_rms = modem.Plot_RMS_Maps(r"c:\Users\jpeacock\Google Drive\Antarctica\ModEM\sm500\ant_sm500_err03_NLCG_062.res")
#p_rms.subplot_hspace = .02
#p_rms.marker = 'o'
#p_rms.fig_size = [6.2, 6.75]
#p_rms.subplot_right = .88
#
#p_rms.save_path = r"c:\Users\jpeacock\Google Drive\Antarctica\figures"
##p_rms.plot_loop(fig_format='pdf')
#p_rms.period_index = 0
#p_rms.redraw_plot()
#p_rms.fig.clf()
#p_rms.plot_loop(fig_format='pdf')

#fig = plt.figure(1, [6, 6], dpi=300)
#ax = fig.add_subplot(1, 1, 1, aspect='equal')
#ax.grid(zorder=3, color=(.75, .75, .75))
#
#for s_arr in data_obj.station_locations:
#    ax.scatter(s_arr['lon'], s_arr['lat'], 
#               marker='v',
#               s=10,
#               c='k')
#    ax.text(s_arr['lon'], s_arr['lat']*1.0001, s_arr['station'][2:],
#            ha='center',
#            va='baseline',
#            fontdict={'size':6})
#            
#ax.tick_params(direction='out')
#
#
#ax.set_xlabel('Longitude (deg)', fontdict={'size':10, 'weight':'bold'})
#ax.set_ylabel('Longitude (deg)', fontdict={'size':10, 'weight':'bold'})
#ax.xaxis.set_major_formatter(FormatStrFormatter('%2.2f'))
#ax.yaxis.set_major_formatter(FormatStrFormatter('%2.2f'))
#
#ax.xaxis.set_major_locator(MultipleLocator(.1))
#ax.yaxis.set_major_locator(MultipleLocator(.1))
#
#[line.set_zorder(200) for line in ax.lines]
#plt.show()

lines = []
for ii in range(0, data_obj.station_locations.size, 2):
    s1 = data_obj.station_locations[ii]['station']
    s2 = data_obj.station_locations[ii+1]['station']
    lines.append(r'\begin{picture}(1, 1)')
    gline = r'\put(0,-300){\includegraphics[width=\textwidth]{figures/'
    gline += 'Supp_{0}_modem_resp_res.pdf'.format(s1)
    gline += r'}}'
    lines.append(gline)
    
    gline = r'\put(0,-625){\includegraphics[width=\textwidth]{figures/'
    gline += 'Supp_{0}_modem_resp_res.pdf'.format(s2)
    gline += r'}}'
    lines.append(gline)
    lines.append(r'\end{picture}')
    lines.append(r'\newpage')
    lines.append('')
    
with open(r"c:\Users\jpeacock\Google Drive\LV_Geothermal\figures\figure_lines.txt", 'w') as fid:
    fid.write('\n'.join(lines))
    