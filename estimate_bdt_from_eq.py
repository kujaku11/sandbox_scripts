# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 10:00:44 2021

@author: jpeacock
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MultipleLocator
from mtpy.modeling import modem

mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_topo_inv_02\st_z05_t02_c03_084.rho"
eq_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\usgs_eq_catalog.csv"
mpad = 25
xmax = 1150
eq_df = pd.read_csv(eq_fn)

m = modem.Model()
m.read_model_file(mfn)
m.res_model[m.res_model > 1e6] = np.nan
med_res = np.nanmedian(m.res_model[mpad:-mpad, mpad:-mpad, :], axis=(0, 1))

fig = plt.figure(3, dpi=300)
fig.clf()

gs = GridSpec(1, 5, wspace=0.1, left=0.08, top=0.87, right=0.985, bottom=0.135)
ax = fig.add_subplot(gs[0:4])

cm = plt.cm.get_cmap("RdYlBu_r")

bins = np.linspace(-2, 40)
n, bins, patches = ax.hist(
    eq_df.depth,
    bins=bins,
    color=(1, 0.53, 0.1),
    edgecolor=(0.5, 0.3, 0.1),
    orientation="horizontal",
)
# n, bins, patches = ax.hist(eq_df.magnitude, 20, color='green', orientation="horizontal")
# To normalize your values
# col = (n-n.min())/(n.max()-n.min())
# for c, p in zip(col, patches):
#     plt.setp(p, 'facecolor', cm(c))

mag = np.zeros(bins.size - 1)
mag_min = np.zeros_like(mag)
mag_max = np.zeros_like(mag)
for ii, b in enumerate(bins[:-1]):
    layer_df = eq_df[(eq_df.depth >= b) & (eq_df.depth <= bins[ii + 1])]
    mag[ii] = layer_df.magnitude.median()
    mag_min[ii] = layer_df.magnitude.min()
    mag_max[ii] = layer_df.magnitude.max()

# ax.fill_between([0, 800], [13, 13], [17, 17], cmap="grays")
grad = np.atleast_2d(np.linspace(0.5, 1, 256)).T
ax.imshow(grad[::-1], extent=[0, xmax, 11, 15], aspect="auto", zorder=0, cmap="Greys")
ax.imshow(grad, extent=[0, xmax, 15, 19], aspect="auto", zorder=0, cmap="Greys")
ax.plot([0, xmax], [15, 15], color="w", lw=1, ls="-.", zorder=1)
ax.text(
    550,
    17,
    "Brittle-Ductile Transition",
    va="top",
    fontdict={"weight": "bold", "size": 12},
)

ax.imshow(grad[::-1], extent=[0, xmax, 21, 25], aspect="auto", zorder=0, cmap="Greys")
ax.imshow(grad, extent=[0, xmax, 25, 29], aspect="auto", zorder=0, cmap="Greys")
ax.plot([0, xmax], [25, 25], color="w", lw=1, ls="--", zorder=1)
ax.text(650, 27, "Moho", va="top", fontdict={"weight": "bold", "size": 12})

# ax.plot(mag*100, bins[:-1], lw=2, color='k')
# ax.plot(mag_min*100, bins[:-1], lw=2, color=(.75, .75, .75))
# ax.plot(mag_max*100, bins[:-1], lw=2, color=(.75, .75, .75))

ax2 = plt.twiny(ax)
ax2.step(med_res, (m.grid_z[0:-1] / 1000.0), color=(0.15, 0.35, 0.85), lw=3)
ax2.set_xscale("log")
ax2.set_xlim(8, 600)
ax2.set_xlabel("Resistivity ($\Omega \cdot m$)")
# ax2.semilogx([40, 40], [11, 19], )
# ax2.semilogx([110, 110], [11, 19], )

ax.set_ylim(30, -0.5)
ax.set_xlim(0, xmax)
ax.yaxis.set_major_locator(MultipleLocator(5))
ax.yaxis.set_minor_locator(MultipleLocator(1))
ax.set_ylabel("Depth (km)")
ax.set_xlabel("Number of Earthquakes")

ax3 = fig.add_subplot(gs[4])
(l1,) = ax3.plot(mag, bins[:-1], color=(0.95, 0.1, 0.2))
ax3.fill_betweenx(bins[:-1], mag_min, mag_max, color=(0.5, 0.25, 0.25))

ax3.plot([-2, 5], [15, 15], color="w", lw=1, ls="-.")
ax3.plot([-2, 5], [25, 25], color="w", lw=1, ls="--")

ax3.grid(which="major", lw=0.5, zorder=0, color=(0.5, 0.5, 0.5))
# ax3.set_axisbelow(True)

ax3.set_xlim(-1.5, 5)
ax3.set_ylim(30, -0.5)
ax3.yaxis.set_major_locator(MultipleLocator(5))
ax3.yaxis.set_minor_locator(MultipleLocator(1))
ax3.xaxis.set_major_locator(MultipleLocator(1))
ax3.xaxis.set_minor_locator(MultipleLocator(0.2))
ax3.set_facecolor((0.75, 0.75, 0.75))
ax3.set_xlabel("Magnitude")
ax3.set(yticklabels=[])
ax3.legend([l1], ["Median"], loc="lower left", prop={"size": 7})

fig.tight_layout()
plt.show()
