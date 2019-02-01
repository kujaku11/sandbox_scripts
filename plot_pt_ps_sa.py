# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 14:49:06 2018

@author: jpeacock
"""

import os
import mtpy.imaging.mtplot as mtplot

#edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\saudi_edi_geographic"
edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\saudi_edi_N30W_shifted\edited\geographic_north"

line_list = ['med1', 'med3', 'med5']

for line in line_list:
    edi_list = [os.path.join(edi_path, fn) for fn in os.listdir(edi_path)
                if fn[0:4] == line]
    
    ps = mtplot.plot_pt_pseudosection(fn_list=edi_list, plot_tipper='yri', fig_num=2)
    ps.ellipse_size = 10
    ps.ellipse_cmap = 'mt_seg_bl2wh2rd'
    ps.ellipse_range = (-6, 6, 3)
    ps.arrow_size = 80
    ps.arrow_lw = .75
    ps.arrow_head_length = 0.25
    ps.arrow_head_width = 0.25
    ps.arrow_threshold = 0.35
    ps.station_id = [3,7]
    ps.ystretch = 50
    ps.xstretch = 475
    
    ps.plot()
    ps.save_figure(r"c:\Users\jpeacock\OneDrive - DOI\med_report\med_pt_ps_line{0}00.png".format(line),
                   fig_dpi=600, close_plot='n')