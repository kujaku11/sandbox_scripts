# -*- coding: utf-8 -*-
"""
Created on Fri Jan  2 13:04:00 2015

@author: jpeacock
"""

import matplotlib.pyplot as plt
import numpy as np

x = np.arange(50)
y = 0.5 * x + 1

fig = plt.figure(1)
ax = fig.add_subplot(1, 1, 1)
(l1,) = ax.plot(x, y)

fig.show()
