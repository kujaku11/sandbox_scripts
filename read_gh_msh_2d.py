# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 15:35:49 2017

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt
import mtpy.modeling.modem as modem
import mtpy.utils.gis_tools as gis_tools
from matplotlib.ticker import MultipleLocator
import mtpy.imaging.mtcolors as mtcolors

# =============================================================================
# Parameters
# =============================================================================
class Center(object):
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    @property
    def easting(self):
        e, n, z = gis_tools.project_point_ll2utm(self.lat, self.lon)
        return e

    @property
    def northing(self):
        e, n, z = gis_tools.project_point_ll2utm(self.lat, self.lon)
        return n


msh_center = Center(46.1912, -122.1944)
model_center = Center(46.450, -122.0320)

# =============================================================================
# Read in Graham's Model
# =============================================================================
gh_fn = (
    r"c:\Users\jpeacock\Documents\iMush\modem_inv\paul_final_model\Hill_2D\MSH_Adams_2D"
)
gh_model = np.loadtxt(gh_fn)

x = (np.array(sorted(list(set(gh_model[:, 0])))) - msh_center.easting) / 1000.0
y = np.array(sorted(list(set(gh_model[:, 1])))) / 1000.0 * -1

gh_res = gh_model[:, 2].reshape((y.size, x.size))

gh_x_grid, gh_y_grid = np.meshgrid(x, y)

# =============================================================================
# Read in Paul's model
# =============================================================================
pb_fn = r"c:\Users\jpeacock\Documents\iMush\modem_inv\paul_final_model\Z4T3_cov0p2x2_L1E2_NLCG_061.rho"

m_obj = modem.Model()
m_obj.read_model_file(pb_fn)

# pick out the correct slice
msh_index = np.where(m_obj.grid_north == -28000)[0][0]

# shift east to match being centered on MSH
east_diff = msh_center.easting - model_center.easting - 500
pb_x_grid, pb_y_grid = np.meshgrid(
    (m_obj.grid_east[0:-1] - east_diff) / 1000.0, m_obj.grid_z[0:-1] / 1000.0
)
pb_res = m_obj.res_model[msh_index, :, :].T

# =============================================================================
# Read in seismicity
# =============================================================================
s_fn = r"c:\Users\jpeacock\Documents\iMush\eq_events_m1_paul.txt"
eq_arr = np.loadtxt(
    s_fn,
    usecols=(0, 2, 3, 4, 5, 6),
    dtype={
        "names": ("mag", "lat", "lon", "depth", "northing", "easting"),
        "formats": ("f8", "f8", "f8", "f8", "f8", "f8"),
    },
)
eq_arr = eq_arr[
    np.where(
        (eq_arr["northing"] > msh_center.northing - 1000)
        & (eq_arr["northing"] < msh_center.northing + 1000)
        & (eq_arr["mag"] > 1.1)
    )
]

# =============================================================================
# Read in long period data
# =============================================================================
lp_fn = r"c:\Users\jpeacock\Documents\iMush\DLP_Wes_ew.txt"
lp_arr = np.loadtxt(
    lp_fn,
    delimiter=",",
    skiprows=1,
    usecols=(2, 3, 4, 5),
    dtype={
        "names": ("east", "north", "depth", "mag"),
        "formats": ("f8", "f8", "f8", "f8"),
    },
)
lp_arr = lp_arr[
    np.where(
        (lp_arr["north"] > msh_center.northing - 5000)
        & (lp_arr["north"] < msh_center.northing + 5000)
    )
]
# =============================================================================
# Plot the 2 models together
# =============================================================================
font_dict = {"size": 10, "weight": "medium"}
plt.rcParams["font.size"] = 7

fig = plt.figure(1, [6.5, 6], dpi=300)
fig.subplots_adjust(hspace=0.12, left=0.01, right=0.92, bottom=0.12, top=0.9)

## --> plot GH model
ax_gh = fig.add_subplot(2, 1, 1, aspect="equal")
im_gh = ax_gh.pcolormesh(
    gh_x_grid, gh_y_grid, np.log10(gh_res), cmap=mtcolors.mt_rd2gr2bl, vmin=-1, vmax=4
)

# turn off tick label on bottom
ax_gh.tick_params(labelbottom="off")

## --> plot imush model
ax_pb = fig.add_subplot(2, 1, 2, aspect="equal")
im_pb = ax_pb.pcolormesh(
    pb_x_grid, pb_y_grid, np.log10(pb_res), cmap=mtcolors.mt_rd2gr2bl, vmin=-1, vmax=4
)

##--> format axes the same
for ax in [ax_gh, ax_pb]:
    ax.scatter(
        (eq_arr["easting"] - msh_center.easting) / 1000.0,
        eq_arr["depth"] + 2.25,
        marker=".",
        c="k",
        s=1,
    )
    ax.scatter(
        (lp_arr["east"] - msh_center.easting) / 1000.0,
        lp_arr["depth"] + 2.25,
        marker="*",
        c="k",
        s=5,
    )
    ax.set_ylabel("depth (km)", fontdict=font_dict)
    ax.set_xlim(-20, 60)
    ax.set_ylim(40, 0)
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(1))
    ax.tick_params(which="minor", width=0.5)
    ax.tick_params(which="both", right="on")
#    ax.tick_params(which='both',
#                   #right='off', left='off', bottom='off', top='off',
#                   labelbottom='off', labeltop='off', labelleft='off',
#                   labelright='off')

ax_pb.set_xlabel("distance (km)", fontdict=font_dict)

## make colorbar
cb_ax = fig.add_axes([0.83, 0.30, 0.03, 0.5])
cb = plt.colorbar(im_gh, cax=cb_ax)
cb.set_label("resistivity (Ohm-m)", fontdict=font_dict)
cb.set_ticks([-1, 0, 1, 2, 3, 4])
cb.set_ticklabels(
    ["$10^{-1}$", "$10^{0}$", "$10^{1}$", "$10^{2}$", "$10^{3}$", "$10^{4}$"]
)
cb.update_ticks()
plt.show()

fig.savefig(
    r"c:\Users\jpeacock\Documents\iMush\Figures\msh_compare_gh_no_labels.png", dpi=900
)
