# -*- coding: utf-8 -*-
"""
Created on Mon Mar 02 16:52:09 2015

@author: jpeacock-pr
"""

import matplotlib.pyplot as plt
import os
import mtpy.modeling.modem_new as modem
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

dfn = dfn = r"c:\MinGW32-xy\Peacock\ModEM\WS_StartingModel_03_tipper\mb_data_tipper.dat"
image_fn = r"c:\Users\jpeacock-pr\Google Drive\JVG\mb_station_base_map_300dpi.jpg"

d_obj = modem.Data()
d_obj.read_data_file(dfn)
fs = 5



fig = plt.figure(1, [5, 2.25], dpi=300)
fig.set_tight_layout(True)
ax = fig.add_subplot(1, 1, 1, aspect='equal')


                 
for s_arr in d_obj.station_locations:
    l1 = ax.scatter(s_arr['lon'], 
                     s_arr['lat'],
                     marker='v',
                     s=15,
                     c='k')
    ax.text(s_arr['lon'],
            s_arr['lat']+.004,
            s_arr['station'][2:],
            horizontalalignment='center',
            verticalalignment='baseline',
            fontdict={'size':fs})
im = plt.imread(image_fn)
ax.imshow(im, aspect='equal', origin='upper', 
          extent=(-119.11, -118.75, 37.8, 37.95)) # 

ax.set_xlabel('Longitude (deg)', fontdict={'size':fs+2, 'weight':'bold'})
ax.set_ylabel('Latitude (deg)', fontdict={'size':fs+2, 'weight':'bold'})
ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
ax.xaxis.set_major_locator(MultipleLocator(.05))
ax.yaxis.set_major_locator(MultipleLocator(.05))
#ax.grid(which='major', color=(.75, .75, .75), linewidth=.75)

ax.set_xlim(-119.11, -118.75)
ax.set_ylim(37.8, 37.95)

#for line in ax.lines:
#    line.set_zorder(10)
plt.show()

fig.savefig(r"c:\Users\jpeacock-pr\Google Drive\JVG\mb_station_map.pdf",
            dpi=300)

                
                