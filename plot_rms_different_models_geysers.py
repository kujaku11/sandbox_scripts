# -*- coding: utf-8 -*-
"""
Plot changes in rms between models

Created on Fri Nov  2 14:24:01 2018

@author: jpeacock
"""
import os
import matplotlib.pyplot as plt
import mtpy.modeling.modem as modem
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Rectangle

plt.rcParams["font.size"] = 16
fs = 18

res_fn_01 = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\modem_inv\inv03\gz_err03_cov02_NLCG_057.res"
res_fn_02 = (
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\modem_inv\inv03\gz_magma_3ohmm.res"
)
sv_path = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\jvgr\figures"
sv_basename = os.path.basename(res_fn_02)[0:-4]

r1 = modem.Residual()
r1.read_residual_file(res_fn_01)

r2 = modem.Residual()
r2.read_residual_file(res_fn_02)

delta_rms = (
    np.abs(r2.residual_array["z"]) / r2.residual_array["z_err"]
    - np.abs(r1.residual_array["z"]) / r1.residual_array["z_err"]
)

### plot change in RMS for each response
fig = plt.figure(1, [12, 8])
fig.clf()

ax1 = fig.add_subplot(1, 1, 1)

legend_list = []
for ii, s_arr in enumerate(r1.residual_array):
    c = float(ii) / len(r1.residual_array)
    line_color = (c, 1 - c, 1 - c)
    (l1,) = ax1.semilogx(
        r1.period_list,
        np.round(delta_rms[ii].mean(axis=(1, 2)), decimals=3),
        color=line_color,
    )
    legend_list.append(l1)

ax1.legend(legend_list, r1.residual_array["station"], loc="upper left", ncol=5)
ax1.set_xlabel("period (s)", fontdict={"size": fs, "weight": "bold"})
ax1.set_ylabel("$\Delta$ RMS", fontdict={"size": fs, "weight": "bold"})
ax1.grid(which="both", color=(0.5, 0.5, 0.5), ls="--")
ax1.set_axisbelow(True)
fig.tight_layout()

### plot map of RMS change
fig_02 = plt.figure(2, [10, 6])
fig_02.clf()

ax2 = fig_02.add_subplot(1, 1, 1, aspect="equal")

r = Rectangle(
    (-122.825, 38.825), 0.05, 0.03, color=(0.5, 0.5, 0.5), alpha=0.75, zorder=0
)
ax2.add_patch(r)

# m_list = []
# m_label = []
c_max = np.nanmax(np.abs(delta_rms[np.nonzero(delta_rms)]))
for ii, s_arr in enumerate(r1.residual_array):

    s_rms = np.nanmean(delta_rms[ii][8:])
    if abs(s_rms) < 0.05:
        s_rms = 0.0

    c = s_rms / c_max
    # print('{0} - {1:.2f} {2:.3f}'.format(s_arr['station'], s_rms, c))
    if c < 0 and c > -0.5:
        line_color = (0.15, 0.75, 1)
    elif c <= -0.5 and c > -1:
        line_color = (0, 0.45, 1)
    elif c <= -1 and c > -1.5:
        line_color = (0, 0.25, 1)
    elif c < -1.5:
        line_color = (0, 0, 0.75)
    elif s_rms >= 0 and s_rms < 0.5:
        line_color = (1, 1, 0.5)
    elif s_rms >= 0.5 and s_rms < 1:
        line_color = (1, 1, 0)
    elif s_rms > 1 and s_rms < 1.5:
        line_color = (1, 0.75, 0.1)
    elif s_rms > 1.5 and s_rms < 2.0:
        line_color = (1, 0.55, 0.0)
    elif s_rms > 2.0 and s_rms < 2.5:
        line_color = (1, 0.25, 0)
    elif s_rms > 2.5 and s_rms < 3:
        line_color = (1, 0, 0)
    elif s_rms > 3 and s_rms < 3.5:
        line_color = (0.7, 0, 0)
    elif s_rms > 3.5:
        line_color = (0.45, 0, 0)
    m1 = ax2.scatter(s_arr["lon"], s_arr["lat"], marker="o", s=380, c=[line_color])
    #        m1, = ax2.plot([None, None], color=line_color)

    #    m_list.append(m1)
    #    m_label.append('{0}  {1:.2f}'.format(s_arr['station'], s_rms))
    #    ax2.text(s_arr['lon'],
    #             s_arr['lat']+.005,
    #             '{0}'.format(s_arr['station']),
    #             horizontalalignment='center',
    #             verticalalignment='top')

    ax2.text(
        s_arr["lon"],
        s_arr["lat"],
        "{0:.1f}".format(np.round(s_rms, decimals=1)),
        horizontalalignment="center",
        verticalalignment="center",
        fontdict={"size": 12},
    )

# ax2.legend(m_list, m_label, loc='lower left', ncol=2)
ax2.set_xlabel("longitude (deg)", fontdict={"size": fs, "weight": "bold"})
ax2.set_ylabel("latitude (deg)", fontdict={"size": fs, "weight": "bold"})
ax2.grid(which="both", color=(0.5, 0.5, 0.5), ls="--")
ax2.set_axisbelow(True)
ax2.xaxis.set_major_locator(MultipleLocator(0.02))
ax2.yaxis.set_major_locator(MultipleLocator(0.02))
fig_02.tight_layout()

# ax2.set_xlim((-107.225, -107.325))
# ax2.set_ylim((33.10, 33.25))


fig.savefig(os.path.join(sv_path, sv_basename + "_responses.png"), dpi=600)
fig_02.savefig(os.path.join(sv_path, sv_basename + "_map.png"), dpi=600)

plt.show()
