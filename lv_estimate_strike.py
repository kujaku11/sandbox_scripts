# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 14:03:40 2016

@author: jpeacock
"""

import os
import mtpy.imaging.mtplot as mtplot
import mtpy.imaging.plotstrike2d as plotstrike2d

edi_path = r"c:\Users\jpeacock\Google Drive\Mono_Basin\INV_EDI_FILES"

edi_list = []
for edi in [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi') == True]:
                
    if os.path.basename(edi).find('LV') == 0:
        edi_list.append(edi)
        continue
    
    if int(os.path.basename(edi)[2:4]) > 15:
        edi_list.append(edi)
        continue
    
#st = mtplot.plot_strike(fn_list=edi_list, plot_yn='n')
#st.plot_tipper = 'y'
#st.fold = False
#st.plot_type = 1
#st.plot()
st = plotstrike2d.PlotStrike2D(fn_list=edi_list, plot_yn='n')
st.plot_tipper = 'y'
st.fold = False
st.plot_type = 1
st.fig_num = 2
st.rot_z = 13.0
st.plot()
                
