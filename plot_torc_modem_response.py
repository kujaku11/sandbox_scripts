# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 11:58:23 2015

@author: jpeacock-pr
"""

import mtpy.modeling.modem as modem
import os

dfn = r"c:\Users\jpeacock\Downloads\torc_modem_data_ef07.dat"
rfn = r"c:\Users\jpeacock\Downloads\torc_z07_c04_NLCG_083.dat"
sv_path = r"c:\Users\jpeacock\Downloads"

data_obj = modem.Data()
data_obj.read_data_file(dfn)

station_list = data_obj.station_locations.station

pr = modem.PlotResponse(data_fn=dfn, resp_fn=rfn, 
                        plot_type=station_list[0],
                        fig_size=[6, 3.25],
                        ms=2, 
                        subplot_bottom=.12,
                        subplot_left=.07,
                        font_size=5.7, 
                        plot_z=False, 
                        plot_yn='n')

               
for ss in station_list:
    pr.legend_loc = 'upper left'
    pr.legend_pos = None
    pr.plot_type = ss
    pr.redraw_plot()
    
    pr.save_figure(save_fn=os.path.join(sv_path, 
                    'Supp_{0}_resp.pdf'.format(ss)),
                    fig_dpi=600)