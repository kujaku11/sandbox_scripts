# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 17:27:06 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np
from matplotlib import pyplot as plt

# =============================================================================
x = np.array(
    [0, -135, -135, -135, -135, -135, -135, -135, 75, 75, 75, 75] * 20
)
y = (90 - x) % 360

fig = plt.figure(1)

ax1 = fig.add_subplot(1, 2, 1, polar=True)
hist = np.histogram(x % 360, bins=int(360 / 5), range=(0, 360))
ax1.bar(np.deg2rad(hist[1][:-1]), hist[0], width=np.deg2rad(5))


ax2 = fig.add_subplot(1, 2, 2, polar=True)
hist = np.histogram(y, bins=int(360 / 5), range=(0, 360))
ax2.bar(np.deg2rad(hist[1][:-1]), hist[0], width=np.deg2rad(5))

plt.show()
