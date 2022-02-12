# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 10:57:29 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as colors
from matplotlib import colorbar as mcb
from matplotlib import image
from matplotlib import gridspec
from mtpy.modeling.modem import Residual

rfn = (
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_01\gb_z03_t02_c02_046.res"
)
im_fn = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\Figures\mp_st_basemap.png"


r = Residual(residual_fn=rfn)
r.read_residual_file()
r.get_rms()
dx = 0.00180
dy = 0.00180
label_dict = {"size": 14, "weight": "bold"}
line_dict = {
    0: {"label": "$Z_{xx}$", "color": (0.25, 0.5, 0.75)},
    1: {"label": "$Z_{xy}$", "color": (0.25, 0.25, 0.75)},
    2: {"label": "$Z_{yx}$", "color": (0.75, 0.25, 0.25)},
    3: {"label": "$Z_{yy}$", "color": (0.75, 0.5, 0.25)},
}

rms_cmap_dict = {
    "red": ((0.0, 1.0, 1.0), (0.2, 1.0, 1.0), (1.0, 0.0, 0.0)),
    "green": ((0.0, 0.0, 0.0), (0.2, 1.0, 1.0), (1.0, 0.0, 0.0)),
    "blue": ((0.0, 0.0, 0.0), (0.2, 1.0, 1.0), (1.0, 0.0, 0.0)),
}
rms_cmap = colors.LinearSegmentedColormap("rms_cmap", rms_cmap_dict, 256)

plt.rcParams["figure.subplot.left"] = 0.05
plt.rcParams["figure.subplot.right"] = 0.99
plt.rcParams["figure.subplot.bottom"] = 0.09
plt.rcParams["figure.subplot.top"] = 0.99

fig = plt.figure(1, dpi=150, figsize=[10.74, 6.32])
fig.clf()

gs1 = gridspec.GridSpec(2, 2, hspace=0.25, wspace=0.075)
gs2 = gridspec.GridSpecFromSubplotSpec(
    4, 1, subplot_spec=gs1[1, 0], hspace=0.01, wspace=0.01
)
gs3 = gridspec.GridSpecFromSubplotSpec(
    4, 1, subplot_spec=gs1[1, 1], hspace=0.01, wspace=0.01
)
ax1 = fig.add_subplot(gs1[0, :], aspect="equal")
ax2 = fig.add_subplot(gs1[1, 0])
# ax3 = fig.add_subplot(gs1[1, 1], sharey=ax2)

# im = image.imread(im_fn)
# ax1.imshow(im, extent=(-115.7425, -115.258, 35.39, 35.565))
# ax1.set_xlim((-115.72, -115.275))
# ax1.set_ylim((35.41, 35.5475))
ax2_list = []
ax3_list = []
line_list = []
for ii in range(2):
    for jj in range(2):
        ax1.scatter(
            r.rms_array["lon"][:] + (dx * (-1) ** (ii)),
            r.rms_array["lat"][:] + (dy * (-1) ** (jj)),
            c=r.rms_array["rms_z_component"][:, ii, jj],
            marker="s",
            s=30,
            edgecolors=(0, 0, 0),
            cmap=rms_cmap,
            norm=colors.Normalize(vmin=0, vmax=5),
        )

        plot_num = 2 * (ii) + (jj)
        # ax2 = fig.add_subplot(gs2[plot_num, 0])
        (l1,) = ax2.plot(
            r.period_list,
            np.nanmean(r.rms_array["rms_z_component_period"][:, :, ii, jj], axis=0),
            color=line_dict[plot_num]["color"],
        )
        ax2.set_xscale("log")
        ax2_list.append(ax2)
        line_list.append(l1)

        ax3 = fig.add_subplot(gs3[plot_num, 0], sharey=ax2)
        rms_sort = np.sort(r.rms_array, order="lon")
        ax3.plot(
            range(r.rms_array.shape[0]),
            rms_sort["rms_z_component"][:, ii, jj],
            color=line_dict[plot_num]["color"],
        )
        ax3.plot(
            range(r.rms_array.shape[0]),
            np.repeat(2.43, r.rms_array.shape[0]),
            color="k",
            ls="--",
            lw=2,
            zorder=1,
        )
        ax3.set_xticks(np.arange(r.rms_array.size, step=2))
        ax3.set_yticklabels(["", "1", "", "2", "", "3"])
        ax3.grid(which="major", color=(0.5, 0.5, 0.5), lw=0.5)
        ax3.set_axisbelow(True)
        ax3.set_xlim((0, r.rms_array.shape[0]))

        ax3_list.append(ax3)
        print(plot_num)
        if plot_num < 4:
            # ax2.set_xticklabels([])
            ax3.set_xticklabels([])

        # else:
        # ax2.set_xlabel("Period (s)", fontdict=label_dict)
        # ax3.set_xticks(np.arange(r.rms_array.size, step=2))
        # ax3.set_xticklabels(rms_sort["station"][np.arange(r.rms_array.size, step=2)],
        #                     fontdict={"rotation": 90})
        # ax3.set_xlabel("Station", fontdict={"size": 12})


# ax1.grid(which="major", color=(.5, .5, .5), lw=.5)
ax1.set_axisbelow(True)
ax1.set_xlabel("Longitude (deg)", fontdict=label_dict)
ax1.set_ylabel("Latitude (deg)", fontdict=label_dict)

ax2.set_ylim(0.51, 3.49)
ax2.plot(
    r.period_list,
    np.repeat(2.43, r.period_list.size),
    color="k",
    ls="--",
    lw=1,
    zorder=1,
)
ax2.grid(which="major", color=(0.5, 0.5, 0.5), lw=0.5)
ax2.grid(which="minor", color=(0.65, 0.65, 0.65), lw=0.35, ls="--")
ax2.set_axisbelow(True)
ax2.legend(
    line_list,
    [line_dict[ii]["label"] for ii in range(4)],
    loc="upper right",
    prop=label_dict,
    borderaxespad=0.05,
    ncol=4,
)
ax2.set_xlim((r.period_list.min(), r.period_list.max()))

ax2.set_xlabel("Period (s)", fontdict=label_dict)
ax2.set_ylabel("RMS", fontdict=label_dict)

# cb_ax = mcb.make_axes(ax, orientation='vertical', fraction=.1)
cb_ax = fig.add_axes([0.93, 0.65, 0.0175, 0.25])
color_bar = mcb.ColorbarBase(
    cb_ax,
    cmap=rms_cmap,
    norm=colors.Normalize(vmin=0, vmax=5),
    orientation="vertical",
)

color_bar.set_label("RMS", fontdict=label_dict)


# ax3.set_xticks(np.arange(r.rms_array.size, step=2))
# ax3.set_xticks(np.arange(r.rms_array.size, step=2))
# ax3.set_xticklabels(rms_sort["station"][np.arange(r.rms_array.size, step=2)],
#                     fontdict={"rotation": 90})
# ax3.set_xlabel((" " * 20).join(["West", "Middle", "East"]), fontdict=label_dict)
ax3.set_xlabel("Station", fontdict=label_dict)
# ax3.grid(which="major", color=(.5, .5, .5), lw=.5)
# ax3.set_axisbelow(True)

fig.tight_layout()

plt.show()
