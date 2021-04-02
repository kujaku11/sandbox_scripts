# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 16:11:54 2017

@author: jpeacock
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse

fig, axes = plt.subplots(
    1,
    3,
    sharex=True,
    sharey=True,
    subplot_kw={"adjustable": "box-forced", "aspect": "equal"},
)


ax1 = axes[0]
ell = Ellipse((0, 0), width=10, height=4, angle=45)
ell.set_facecolor((1, 0.5, 0))
ax1.add_artist(ell)


ax2 = axes[1]
ell = Ellipse((0, 0), width=10, height=40, angle=15)
ell.set_facecolor((1, 0.5, 0))
ax2.add_artist(ell)

ax3 = axes[2]
ell = Ellipse((0, 0), width=20, height=10, angle=115)
ell.set_facecolor((1, 0.5, 0))
ax3.add_artist(ell)

ax1.set_ylim((-50, 50))
ax1.set_xlim((-30, 30))

for ax in axes:
    ax.grid(which="major")
# plt.show()
