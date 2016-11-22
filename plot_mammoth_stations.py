# -*- coding: utf-8 -*-
"""
Created on Mon Jun 01 16:20:52 2015

@author: jpeacock-pr
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker 

fn = r"C:\Users\jpeacock-pr\Documents\LV\Maps\MT_stations_2015.txt"

d = np.loadtxt(fn, dtype={'names':('station', 'lon', 'lat'), 
                          'formats':('|S5', 'f4', 'f4')}, 
                    delimiter=',', skiprows=1)

fig = plt.figure(1, [6, 4], dpi=300)
fig.subplots_adjust(left=.1, bottom=.15, right=.98, top=.98)    
fig.clf()
ax = fig.add_subplot(1,1,1, aspect='equal')

for ss in d:
    ax.plot(ss['lon'], ss['lat'], 
            ls='None',
            marker='v',
            mec='k',
            mfc='k',
            ms=5)
    ax.text(ss['lon'], ss['lat']*1.00015, ss['station'][2:],
            horizontalalignment='center',
            verticalalignment='baseline',
            fontdict={'size':8})
            
ax.set_xlabel('Longitude (deg)', fontdict={'size':12, 'weight': 'bold'})
ax.set_ylabel('Latitude (deg)', fontdict={'size':12, 'weight': 'bold'})

ax.grid(color=(.75, .75, .75), which='both')
#[line.set_zorder(3) for line in ax.lines]
ax.xaxis.set_major_locator(ticker.MultipleLocator(.1))
ax.yaxis.set_major_locator(ticker.MultipleLocator(.1))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(.02))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(.02))

ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
ax.set_axisbelow(True)

ax.set_xlim(-119.06, -118.70)
ax.set_ylim(37.52, 37.78)

plt.show()

