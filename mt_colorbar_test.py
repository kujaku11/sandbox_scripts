# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 11:31:38 2015

@author: jpeacock-pr
"""

import matplotlib.colors as colors
import numpy as np
import matplotlib.pyplot as plt


#blue to white to red
#skcmapdict2 = {'red':  ((0.0, 0.0, 0.0),
#                        (0.25,0.0, 0.0),
#                        (0.5, 0.8, 1.0),
#                        (0.75,1.0, 1.0),
#                        (1.0, 0.4, 1.0)),
#
#               'green': ((0.0, 0.0, 0.0),
#                         (0.25,0.0, 0.0),
#                         (0.5, 0.9, 0.9),
#                         (0.75,0.0, 0.0),
#                         (1.0, 0.0, 0.0)),
#
#               'blue':  ((0.0, 0.0, 0.4),
#                         (0.25,1.0, 1.0),
#                         (0.5, 1.0, 0.8),
#                         (0.75,0.0, 0.0),
#                         (1.0, 0.0, 0.0))}
                         
skcmapdict2 = {'red':  ((0.0, 0.5, 0.2),
                        (0.25, 1.0, 1.0),
                        (0.55, 1.0, 1.0),
                        (0.69, 0.9, 0.9),
                        (0.88, 0.2, 0.2),
                        (1.0, 0.2, 0.2)),

               'green': ((0.0, 0.0, 0.0),
                         (0.25, 0.3, 0.3),
                         (0.55, 1.0, 1.0),
                         (0.69, 0.9, 0.9),
                         (0.88, 0.3, 0.3),
                         (1.0, 0.3, 0.3)),

               'blue':  ((0.0, 0.0, 0.0),
                         (0.25, 0.0, 0.0),
                         (0.55, 0.9, 0.9),
                         (0.69, 1.0, 1.0),
                         (0.88, 1.0, 1.0),
                         (1.0, 0.4, 0.75))}
                       
mt_bl2wh2rd = colors.LinearSegmentedColormap('mt_bl2wh2rd', skcmapdict2, 256)

fig1 = plt.figure(1)
fig1.clf()
ax = fig1.add_subplot(1,1,1, aspect='equal')
im1 = ax.imshow(np.random.rand(12,12), cmap=mt_bl2wh2rd, 
                interpolation='nearest')
plt.colorbar(im1, ax=ax)
plt.show()