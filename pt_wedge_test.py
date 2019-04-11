# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 12:06:03 2019

@author: jpeacock
"""
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Ellipse
from matplotlib import colors
from matplotlib import colorbar
from mtpy.core import edi_collection

from mtpy.imaging import mtcolors
import glob

edi_dir = r"c:\Users\jpeacock\Documents\edi_folders\imush_edi"

def add_pt_patch(ax, pt_dict, scale=1, width=3, ascale=1, ecmap='mt_bl2wh2rd_r',
                 scmap='Greys', **kwargs):
    plot_x = pt_dict['lon']
    plot_y = pt_dict['lat'] 
    w1 = Wedge((plot_x, plot_y), 
               scale,
#               90 - pt_dict['azimuth'] - np.nanmin([pt_dict['phi_max_err'], 5]),
#               90 - pt_dict['azimuth'] + np.nanmin([pt_dict['phi_max_err'], 5]),
               90 - pt_dict['azimuth'] - width,
               90 - pt_dict['azimuth'] + width,
               color=mtcolors.get_plot_color(pt_dict['phi_max'], 
                                              'phimax', 
                                              ecmap,
                                              0, 90))
    w2 = Wedge((plot_x, plot_y),
               scale,
#               270 - pt_dict['azimuth'] - np.nanmin([pt_dict['phi_max_err'], 5]),
#               270 - pt_dict['azimuth'] + np.nanmin([pt_dict['phi_max_err'], 5]),
               270 - pt_dict['azimuth'] - width,
               270 - pt_dict['azimuth'] + width,
               color=mtcolors.get_plot_color(pt_dict['phi_max'], 
                                             'phimax', 
                                             ecmap,
                                             0, 90))
    
    w3 = Wedge((plot_x, plot_y), 
               scale * pt_dict['phi_min']/pt_dict['phi_max'],
#               -1*pt_dict['azimuth'] - np.nanmin([pt_dict['phi_min_err'], 5]),
#               -1*pt_dict['azimuth'] + np.nanmin([pt_dict['phi_min_err'], 5]),
               -1 * pt_dict['azimuth'] - width,
               -1 * pt_dict['azimuth'] + width,
               color=mtcolors.get_plot_color(pt_dict['phi_min'], 
                                             'phimin', 
                                             ecmap,
                                             0, 90))
    w4 = Wedge((plot_x, plot_y), 
               scale * pt_dict['phi_min']/pt_dict['phi_max'],
#               180 - pt_dict['azimuth'] - np.nanmin([pt_dict['phi_min_err'], 5]),
#               180 - pt_dict['azimuth'] + np.nanmin([pt_dict['phi_min_err'], 5]),
               180 - pt_dict['azimuth'] - width,
               180 - pt_dict['azimuth'] + width,
               color=mtcolors.get_plot_color(pt_dict['phi_min'], 
                                             'phimin', 
                                             ecmap,
                                             0, 90))
    
    if pt_dict['tip_mag_re'] > 0:
        txr = pt_dict['tip_mag_re'] * ascale * np.sin(np.deg2rad(pt_dict['tip_ang_re']))
        tyr = pt_dict['tip_mag_re'] * ascale * np.cos(np.deg2rad(pt_dict['tip_ang_re']))
    
        ax.arrow(plot_x,
                 plot_y,
                 txr,
                 tyr,
                 width=.075 * ascale,
                 facecolor=(0, 1, 1),
                 edgecolor=(0, 0, 0),
                 length_includes_head=False,
                 head_width=ascale * .25,
                 head_length=scale * .25)
        
        txi = pt_dict['tip_mag_im'] * ascale * np.sin(np.deg2rad(pt_dict['tip_ang_im']))
        tyi = pt_dict['tip_mag_im'] * ascale * np.cos(np.deg2rad(pt_dict['tip_ang_im']))
    
        ax.arrow(plot_x,
                 plot_y,
                 txi,
                 tyi,
                 width=.075 * ascale,
                 facecolor=(1, 0, 1),
                 edgecolor=(0, 0, 0),
                 length_includes_head=False,
                 head_width=ascale * .25,
                 head_length=ascale * .25)
    
    
    # make an ellipse
    e1 = Ellipse((plot_x, plot_y),
                 width=2 * scale,
                 height=2 * scale * pt_dict['phi_min']/pt_dict['phi_max'],
                 angle=90 - pt_dict['azimuth'])
    gm = np.sqrt(abs(pt_dict['phi_min'])**2 + abs(pt_dict['phi_max'])**2)
    
    e1.set_facecolor(mtcolors.get_plot_color(gm, 
                                              'geometric_mean', 
                                              ecmap,
                                              0, 90))
    e1.set_edgecolor(mtcolors.get_plot_color(abs(pt_dict['skew']), 
                                             'skew_seg', 
                                             scmap,
                                             0, 9,
                                             np.arange(0, 12, 3)))
    e1.set_linewidth(4)
    e1.set_alpha(.85)
    ### add patches
    ax.add_patch(e1)
    ax.add_patch(w1)
    ax.add_patch(w2)
    ax.add_patch(w3)
    ax.add_patch(w4)
    #ax.add_patch(w5)
    #ax.add_patch(w6)
    
    return ax

# =============================================================================
# plot
# =============================================================================
edi_list = glob.glob(os.path.join(edi_dir, '*.edi'))
ec = edi_collection.EdiCollection(edilist=edi_list)
scale = .035
e_cmap = 'mt_rd2wh2bl_r'
s_cmap = 'Greys'

pt_list = ec.get_phase_tensor_tippers(10.0)

fig = plt.figure(1)
fig.clf()
ax = fig.add_subplot(1, 1, 1, aspect='equal')
for pt_dict in pt_list:
    ax = add_pt_patch(ax, pt_dict, scale=scale, width=5, ascale=.070,
                      ecmap=e_cmap)
  
bb = ec.get_bounding_box()
ax.set_ylim((bb['MinLat']-scale, bb['MaxLat']+scale))
ax.set_xlim((bb['MinLon']-scale, bb['MaxLon']+scale))
ax.grid()
ax.set_axisbelow(True)

ax.set_xlabel('Longitude (degrees)')
ax.set_ylabel('Latitude (degrees)')

### phase color bar
if e_cmap in list(mtcolors.cmapdict.keys()):
    cmap_input = mtcolors.cmapdict[e_cmap]
else:
    cmap_input = mtcolors.cm.get_cmap(e_cmap)
cbax = fig.add_axes([.9, .60, .015, .25])
cb = colorbar.ColorbarBase(cbax,
                           cmap=cmap_input,#mtcl.cmapdict[cmap],
                           norm=colors.Normalize(vmin=0,
                                                 vmax=90),
                            orientation='vertical')
cb.set_label('Phase (deg)',
              fontdict={'size': 12, 'weight': 'bold'})

### skew colorbar
clist = [(1-cc, 1-cc, 1-cc) for cc in np.arange(0, 1 + 1. / (3), 1. / (3))]

# make segmented colormap
seg_greys = colors.ListedColormap(clist)

# make bounds so that the middle is white
sk_bounds = np.arange(0, 12, 3)

# normalize the colors
sk_norms = colors.BoundaryNorm(sk_bounds, seg_greys.N)

if s_cmap in list(mtcolors.cmapdict.keys()):
    cmap_input = mtcolors.cmapdict[s_cmap]
else:
    cmap_input = mtcolors.cm.get_cmap(s_cmap)
scbax = fig.add_axes([.9, .175, .015, .25])
scb = colorbar.ColorbarBase(scbax,
                            cmap=seg_greys,
                            norm=sk_norms,
                            orientation='vertical')

# label the color bar accordingly
scb.set_label('|Skew (deg)|',
              fontdict={'size': 12, 'weight': 'bold'})

plt.show()
