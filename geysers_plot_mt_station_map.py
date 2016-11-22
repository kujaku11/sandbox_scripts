# -*- coding: utf-8 -*-
"""
Created on Fri Sep 09 11:06:34 2016

@author: jpeacock
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
import numpy as np

fn_map = r"c:\Users\jpeacock\Documents\ClearLake\geological_map_sadowski.png"
fn_stations = r"c:\Users\jpeacock\Documents\ClearLake\Geysers_proposed_mt_sites.txt"

s_arr = np.loadtxt(fn_stations, delimiter=',', skiprows=1, 
                   dtype=[('station', '|S5'), 
                          ('lat', np.float),
                          ('lon', np.float)])

im_arr = plt.imread(fn_map)

fig = plt.figure(1, [6, 6], dpi=150)
fig.clf()
ax = fig.add_subplot(1, 1, 1, aspect='equal')

ax.imshow(im_arr[50:-30, 50:-40, :], 
          extent=(-122.905, -122.662, 38.7165, 38.9),
          aspect='equal',
          alpha=.6)

ax.scatter(s_arr['lon'], s_arr['lat'], marker='o', c='k', s=30)


ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

ax.xaxis.set_major_locator(MultipleLocator(2./60))
ax.yaxis.set_major_locator(MultipleLocator(2./60))
ax.xaxis.set_minor_locator(MultipleLocator(.5/60))
ax.yaxis.set_minor_locator(MultipleLocator(.5/60))
ax.grid(which='major')

ax.set_xlim(-122.904, -122.662)
ax.set_ylim(38.7168, 38.9)

ax.set_xlabel('Longitude (deg)', fontdict={'size':12, 'weight':'bold'})
ax.set_ylabel('Latitude (deg)', fontdict={'size':12, 'weight':'bold'})
#ax.xaxis.set_minor_locator(MultipleLocator(1./60))
#ax.yaxis.set_minor_locator(MultipleLocator(1./60))
plt.show()