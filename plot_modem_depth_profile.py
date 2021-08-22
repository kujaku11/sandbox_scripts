# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 18:24:02 2018

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import mtpy.modeling.modem as modem


# =============================================================================
# Inputs
# =============================================================================
# mfn = r"g:\Camas\Reports\MT\cm_z06_c05_107.rho"
mfn = r"g:\Camas\Reports\MT\cm_086.rho"

drill_hole = {"east": 200, "north": -300}

# =============================================================================
# read model plot drill hole
# =============================================================================
m_obj = modem.Model()
m_obj.read_model_file(mfn)

### locate drill hole
e_index = np.where(
    (m_obj.grid_east <= drill_hole["east"] + 40)
    & (m_obj.grid_east >= drill_hole["east"] - 40)
)[0][0]
n_index = np.where(
    (m_obj.grid_north <= drill_hole["north"] + 40)
    & (m_obj.grid_north >= drill_hole["north"] - 40)
)[0][0]

z_res = m_obj.res_model[n_index, e_index, :]

### make figure
fig = plt.figure(1, [5, 8])
fig.clf()
fig.subplots_adjust(
    top=0.975, bottom=0.08, left=0.155, right=0.875, hspace=0.2, wspace=0.2
)
ax = fig.add_subplot(1, 1, 1)
(l1,) = ax.semilogx(z_res, m_obj.grid_z[0:-1] * 3.25, lw=2)

ax.set_xlabel("Resistivity (Ohm-m)", fontdict={"size": 12, "weight": "bold"})
ax.set_ylabel("Depth (ft)", fontdict={"size": 12, "weight": "bold"})
ax.yaxis.set_major_locator(MultipleLocator(100))
ax.yaxis.set_minor_locator(MultipleLocator(20))
ax.set_xlim((10, 500))
ax.set_ylim((1620, 0))
ax.grid(which="major", ls="--", color=(0.65, 0.65, 0.65), lw=1.2)
ax.grid(which="minor", ls="-.", color=(0.75, 0.75, 0.75), lw=1)


ax2 = plt.twinx(ax)
(l2,) = ax.semilogx(z_res, m_obj.grid_z[0:-1], lw=2, alpha=0)
ax2.set_ylim((500, 0))
ax2.set_xlim((10, 500))
ax2.set_ylabel("Depth (m)", fontdict={"size": 12, "weight": "bold"})
# ax2.grid(which='both', color=(.75, .75, 1), ls='-.')

plt.show()
