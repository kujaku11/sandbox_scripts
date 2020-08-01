# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 11:58:23 2015

@author: jpeacock-pr
"""

import mtpy.modeling.modem as modem
import os
import matplotlib.pyplot as plt

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['font.family'] = 'Tahoma'


dfn = r"d:\Documents\Montserrat\modem_inv\Inv05_dr\mont_data_topo_c_z.dat"
rfn = r"d:\Documents\Montserrat\modem_inv\Inv05_dr\mont_topo_err07_cov04_NLCG_087.dat"
sv_path = r"d:\Documents\Montserrat\figures"

data_obj = modem.Data()
data_obj.read_data_file(dfn)

station_list = data_obj.station_locations.station.copy()
plot_type = 'maps'
file_fmt = 'png'

plot_list = [{'label': r'$Z_{xx}$', 'index': (0, 0), 'plot_num': 1},
             {'label': r'$Z_{xy}$', 'index': (0, 1), 'plot_num': 2},
             {'label': r'$Z_{yx}$', 'index': (1, 0), 'plot_num': 3},
             {'label': r'$Z_{yy}$', 'index': (1, 1), 'plot_num': 4}]

if plot_type == 'maps':
    pm = modem.PlotRMSMaps(rfn[:-4]+'.res',
                           marker='o',
                           marker_size=7,
                           save_path=sv_path,
                           fig_size=[7.38, 4.91],
                           subplot_right=.875,
                           tick_locator=.05,
                           text_pad=.005,
                           subplot_vspace=.07,
                           subplot_left=.1,
                           pad_x=.02,
                           pad_y=.02)
    pm.plot_z_list = plot_list
    pm.redraw_plot()
    pm.plot_loop(fig_format=file_fmt)

if plot_type == 'response':
    pr = modem.PlotResponse(data_fn=dfn, resp_fn=rfn, 
                            plot_type=station_list[0],
                            fig_size=[9, 3.25],
                            ms=2, 
                            subplot_bottom=.12,
                            subplot_left=.05,
                            font_size=5.7,
                            plot_z = False,
                            cted=(0, 0, 0),
                            ctmd=(0, 0, 0),
                            ctem=(0.75, .0, 0.0),
                            ctmm=(0.75, .0, .0),
                            mted='o',
                            mtem='x',
                            mtmm='x',
                            subplot_wspace=.20)
                   
    for ss in station_list:
        pr.plot_type = ss
        pr.redraw_plot()
        pr.save_figure(save_fn=os.path.join(sv_path,
                        'Supp_{0}.{1}'.format(ss, file_fmt)),
                        file_format=file_fmt,
                        fig_dpi=300, close_fig='y')

# \put(0,-110){\includegraphics[width=\textwidth]{figures/Supp_GZ01.pdf}}
#\put(0,-240){\includegraphics[width=\textwidth]{figures/Supp_GZ02.pdf}}
#\put(0,-370){\includegraphics[width=\textwidth]{figures/Supp_GZ03.pdf}}
#\put(0,-500){\includegraphics[width=\textwidth]{figures/Supp_GZ04.pdf}}                   
lines = []
for ii in range(0, data_obj.station_locations.station.size-2, 3):
    s1 = data_obj.station_locations.station[ii]
    s2 = data_obj.station_locations.station[ii+1]
    s3 = data_obj.station_locations.station[ii+2]
    
    lines.append(r'\begin{picture}(1, 1)')
    gline = r'\put(0,-180){\includegraphics[width=\textwidth]{'
    gline += 'Supp_{0}.pdf'.format(s1)
    gline += r'}}'
    lines.append(gline)
    
    gline = r'\put(0,-360){\includegraphics[width=\textwidth]{'
    gline += 'Supp_{0}.pdf'.format(s2)
    gline += r'}}'
    lines.append(gline)
    
    gline = r'\put(0,-540){\includegraphics[width=\textwidth]{'
    gline += 'Supp_{0}.pdf'.format(s3)
    gline += r'}}'
    lines.append(gline)
    
#    gline = r'\put(0,-500){\includegraphics[width=\textwidth]{'
#    gline += 'Supp_{0}.pdf'.format(s4)
#    gline += r'}}'
#    lines.append(gline)
    
    lines.append(r'\end{picture}')
    lines.append(r'\newpage')
    lines.append('')
    
with open(os.path.join(sv_path, "figure_lines.txt"), 'w') as fid:
    fid.write('\n'.join(lines))