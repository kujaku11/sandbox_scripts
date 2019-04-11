# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 12:06:03 2019

@author: jpeacock
"""
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Ellipse
from mtpy.core import mt
from mtpy.core import edi_collection

from mtpy.imaging import mtcolors
import glob

edi_dir = r"c:\Users\jpeacock\Documents\edi_folders\imush_edi"
index = 30

def add_pt_patch(ax, pt_dict, scale=1, **kwargs):
    plot_x = pt_dict['lon']
    plot_y = pt_dict['lat'] 
    w1 = Wedge((plot_x, plot_y), 
               scale,
               90 - pt_dict['azimuth'] - np.nanmin([pt_dict['phi_max_err'], 5]),
               90 - pt_dict['azimuth'] + np.nanmin([pt_dict['phi_max_err'], 5]),
               color=mtcolors.get_plot_color(pt_dict['phi_max'], 
                                              'phimax', 
                                              'mt_rd2wh2bl_r',
                                              0, 90))
    w2 = Wedge((plot_x, plot_y),
               scale,
               270 - pt_dict['azimuth'] - np.nanmin([pt_dict['phi_max_err'], 5]),
               270 - pt_dict['azimuth'] + np.nanmin([pt_dict['phi_max_err'], 5]),
               color=mtcolors.get_plot_color(pt_dict['phi_max'], 
                                             'phimax', 
                                             'mt_rd2wh2bl_r',
                                             0, 90))
    
    w3 = Wedge((plot_x, plot_y), 
               scale * pt_dict['phi_min']/pt_dict['phi_max'],
               -1*pt_dict['azimuth'] - np.nanmin([pt_dict['phi_min_err'], 5]),
               -1*pt_dict['azimuth'] + np.nanmin([pt_dict['phi_min_err'], 5]),
               color=mtcolors.get_plot_color(pt_dict['phi_min'], 
                                             'phimin', 
                                             'mt_rd2wh2bl_r',
                                             0, 90))
    w4 = Wedge((plot_x, plot_y), 
               scale * pt_dict['phi_min']/pt_dict['phi_max'],
               180 - pt_dict['azimuth'] - np.nanmin([pt_dict['phi_min_err'], 5]),
               180 - pt_dict['azimuth'] + np.nanmin([pt_dict['phi_min_err'], 5]),
               color=mtcolors.get_plot_color(pt_dict['phi_min'], 
                                             'phimin', 
                                             'mt_rd2wh2bl_r',
                                             0, 90))
    if pt_dict['skew'] < 0:
        plot_skew = max([-12, pt_dict['skew']])
    else:
        plot_skew = min([12, pt_dict['skew']])
    w5 = Wedge((plot_x, plot_y), 
               scale/3., 
               90 - pt_dict['azimuth'] - plot_skew - 2,
               90 - pt_dict['azimuth'] - plot_skew + 2, 
               color=mtcolors.get_plot_color(plot_skew, 
                                             'skew', 
                                             'mt_yl2rd',
                                             -6, 6,
                                             np.arange(-6, 6, 2)))
    
    w6 = Wedge((plot_x, plot_y), 
               scale, 
               270 - pt_dict['azimuth'] - pt_dict['skew'],
               270 - pt_dict['azimuth'] + pt_dict['skew'], 
               color=mtcolors.get_plot_color(pt_dict['skew'], 
                                             'skew_seg', 
                                             'mt_seg_bl2wh2rd',
                                             -6, 6,
                                             np.arange(-6, 6, 2)))
    
    
    # make an ellipse
    e1 = Ellipse((plot_x, plot_y),
                 width=2 * scale,
                 height=2 * scale * pt_dict['phi_min']/pt_dict['phi_max'],
                 angle=90 - pt_dict['azimuth'])
    e1.set_facecolor(mtcolors.get_plot_color((abs(pt_dict['phi_min']) + 
                                              abs(pt_dict['phi_max']))/2, 
                                              'geometric_mean', 
                                              'mt_rd2wh2bl_r',
                                              0, 90))
    e1.set_edgecolor(mtcolors.get_plot_color(abs(pt_dict['skew']), 
                                             'skew', 
                                             'mt_wh2bl',
                                             0, 6,))
    e1.set_linewidth(2)
    e1.set_alpha(.65)
    ### add patches
    ax.add_patch(e1)
    ax.add_patch(w1)
    ax.add_patch(w2)
    ax.add_patch(w3)
    ax.add_patch(w4)
    ax.add_patch(w5)
    #ax.add_patch(w6)
    
    return ax

# =============================================================================
# plot
# =============================================================================
edi_list = glob.glob(os.path.join(edi_dir, '*.edi'))
ec = edi_collection.EdiCollection(edilist=edi_list)
scale = .025

pt_list = ec.get_phase_tensor_tippers(30.0)

fig = plt.figure(1)
fig.clf()
ax = fig.add_subplot(1, 1, 1, aspect='equal')
for pt_dict in pt_list:
    ax = add_pt_patch(ax, pt_dict, scale=scale)
  
bb = ec.get_bounding_box()
ax.set_ylim((bb['MinLat']-scale, bb['MaxLat']+scale))
ax.set_xlim((bb['MinLon']-scale, bb['MaxLon']+scale))

plt.show()
