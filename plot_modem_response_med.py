# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 11:58:23 2015

@author: jpeacock-pr
"""

import mtpy.modeling.modem as modem
import os

dfn = r"c:\Users\jpeacock\OneDrive - DOI\med_report\data\med_modem_data_z07_t06.dat"
rfn = r"c:\Users\jpeacock\OneDrive - DOI\med_report\data\Med_SS_Z3T2_NLCG_168.dat"
sv_path = r"c:\Users\jpeacock\OneDrive - DOI\med_report\report\figures"

data_obj = modem.Data()
data_obj.read_data_file(dfn)

station_list = data_obj.station_locations.station.copy()

pm = modem.PlotRMSMaps(rfn[:-4]+'.res',
                       marker='o',
                       marker_size=5,
                       save_path=sv_path,
                       fig_size=[4.75, 6],
                       subplot_right=.875,
                       tick_locator=.5,
                       text_pad=.09,
                       subplot_vspace=.1,
                       subplot_left=.15)

pm.plot_loop(fig_format='svg')

#pr = modem.PlotResponse(data_fn=dfn, resp_fn=rfn, 
#                        plot_type=station_list[16],
#                        fig_size=[9, 3.25],
#                        ms=2, 
#                        subplot_bottom=.12,
#                        subplot_left=.05,
#                        font_size=5.7,
#                        plot_z = False,
#                        cted=(0, 0, 0),
#                        ctmd=(0, 0, 0),
#                        ctem=(0.75, .0, 0.0),
#                        ctmm=(0.75, .0, .0),
#                        mted='o',
#                        mtem='x',
#                        mtmm='x',
#                        subplot_wspace=.20)
#               
#for ss in station_list:
#    pr.plot_type = ss
#    pr.redraw_plot()
#    pr.save_figure(save_fn=os.path.join(sv_path,
#                    'Appendix_03_{0}.svg'.format(ss)),
#                    file_format='svg',
#                    fig_dpi=300, close_fig='y')

                    
#lines = []
#for ii in range(0, data_obj.station_locations.station.size-2, 3):
#    s1 = data_obj.station_locations.station[ii]
#    s2 = data_obj.station_locations.station[ii+1]
#    s3 = data_obj.station_locations.station[ii+2]
#    
#    lines.append(r'\begin{picture}(1, 1)')
#    gline = r'\put(0,-212){\includegraphics[width=.92\textwidth]{'
#    gline += 'Supp_{0}_resp.pdf'.format(s1)
#    gline += r'}}'
#    lines.append(gline)
#    
#    gline = r'\put(0,-425){\includegraphics[width=.92\textwidth]{'
#    gline += 'Supp_{0}_resp.pdf'.format(s2)
#    gline += r'}}'
#    lines.append(gline)
#    
#    gline = r'\put(0,-640){\includegraphics[width=.92\textwidth]{'
#    gline += 'Supp_{0}_resp.pdf'.format(s3)
#    gline += r'}}'
#    lines.append(gline)
#    lines.append(r'\end{picture}')
#    lines.append(r'\newpage')
#    lines.append('')
#    
#with open(os.path.join(sv_path, "figure_lines.txt"), 'w') as fid:
#    fid.write('\n'.join(lines))