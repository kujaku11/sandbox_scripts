# -*- coding: utf-8 -*-
"""
Created on Thu Feb 04 16:41:25 2016

@author: jpeacock
"""

import mtpy.modeling.occam2d as occam
import mtpy.imaging.mtcolors as mtcolors

#mfn = r"c:\MinGW32-xy\Peacock\occam\MountainPass\inv01_tm_sm3\ITER60.iter"
#dfn = r"c:\MinGW32-xy\Peacock\occam\MountainPass\inv01_tm_sm3\OccamDataFile_rw.dat"
mfn = r"c:\MinGW32-xy\Peacock\occam\MountainPass\inv04_tm_rot\ITER12.iter"
dfn = r"c:\MinGW32-xy\Peacock\occam\MountainPass\inv04_tm_rot\OccamDataFile.dat"

pm = occam.PlotModel(iter_fn=mfn, data_fn=dfn, plot_yn='n')
pm.ylimits = (-1.5, 10)
pm.cmap = mtcolors.mt_rd2gr2bl
pm.climits = (.9, 4)
pm.station_font_pad = 1.2
pm.station_id = [2, 4]
pm.cb_shrink = .4  
pm.plot()

#pm.save_figure(r"c:\Users\jpeacock\Documents\MountainPass\Figures\mp_tm_sm3_iter60_aseg_2016.jpg",
#               fig_dpi=600)