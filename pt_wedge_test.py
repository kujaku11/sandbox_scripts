# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 12:06:03 2019

@author: jpeacock
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from mtpy.core import mt

m1 = mt.MT(r"c:\Users\jpeacock\Documents\edi_folders\geysers\gz01.edi")
index = 28

fig = plt.figure(1)
fig.clf()
ax = fig.add_subplot(1, 1, 1, aspect='equal')

w1 = Wedge((0, 0), 
           m1.pt.phimax[index]/90.,
           90-m1.pt.azimuth[index]-m1.pt.phimax_err[index],
           90-m1.pt.azimuth[index]+m1.pt.phimax_err[index],
           color=(.8, 0, 0))
w2 = Wedge((0, 0),
           m1.pt.phimax[index]/90.,
           270-m1.pt.azimuth[index]-m1.pt.azimuth_err[index],
           270-m1.pt.azimuth[index]+m1.pt.azimuth_err[index],
           color=(.8, 0, 0))

w3 = Wedge((0, 0), 
           m1.pt.phimin[index]/90.,
           90+m1.pt.azimuth[index]-m1.pt.azimuth_err[index],
           90+m1.pt.azimuth[index]+m1.pt.azimuth_err[index],
           color=(0, 0, .8))
w4 = Wedge((0, 0), 
           m1.pt.phimin[index]/90.,
           270+m1.pt.azimuth[index]-m1.pt.azimuth_err[index],
           270+m1.pt.azimuth[index]+m1.pt.azimuth_err[index],
           color=(0, 0, .8))

w5 = Wedge((0, 0), .1, 90+3, 90+6, color=(0, .8, .8))
w6 = Wedge((0, 0), .1, 270+3, 270+6, color=(0, .8, .8))

ax.add_patch(w1)
ax.add_patch(w2)
ax.add_patch(w3)
ax.add_patch(w4)
ax.add_patch(w5)
ax.add_patch(w6)

ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)

plt.show()
