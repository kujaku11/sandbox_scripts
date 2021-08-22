# -*- coding: utf-8 -*-
"""
Plot changes in rms between models

Created on Fri Nov  2 14:24:01 2018

@author: jpeacock
"""

import matplotlib.pyplot as plt
import mtpy.modeling.modem as modem
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Rectangle

fs = 12
res_fn_01 = r"c:\Users\jpeacock\Documents\SaudiArabia\modem_inv\inv_n30w\med_z03_t02_c03_164.res"
res_fn_02 = (
    r"c:\Users\jpeacock\Documents\SaudiArabia\modem_inv\inv_n30w\med_m_z05_c03_024.res"
)

if res_fn_02.endswith(".dat"):
    d = modem.Residual()
    res_fn_02 = d.calculate_residual_from_data(
        r"c:\Users\jpeacock\Documents\SaudiArabia\modem_inv\inv_n30w\med_modem_data_z03_t02_edit.dat",
        res_fn_02,
    )


r1 = modem.Residual()
r1.read_residual_file(res_fn_01)

r2 = modem.Residual()
r2.read_residual_file(res_fn_02)

delta_rms = (
    np.abs(r2.residual_array["z"]) / r2.residual_array["z_err"]
    - np.abs(r1.residual_array["z"]) / r2.residual_array["z_err"]
)

fig = plt.figure(1, [12, 8])
fig.clf()

ax1 = fig.add_subplot(1, 1, 1)

legend_list = []
for ii, s_arr in enumerate(r1.residual_array):
    c = float(ii) / len(r1.residual_array)
    line_color = (c, 1 - c, 1 - c)
    (l1,) = ax1.semilogx(
        r1.period,
        np.round(delta_rms[ii].mean(axis=(1, 2)), decimals=3),
        color=line_color,
    )
    legend_list.append(l1)

ax1.legend(legend_list, r1.residual_array["station"], loc="lower left", ncol=5)
ax1.set_xlabel("period (s)", fontdict={"size": fs, "weight": "bold"})
ax1.set_ylabel("$\Delta$ RMS", fontdict={"size": fs, "weight": "bold"})
ax1.grid(which="both", color=(0.5, 0.5, 0.5), ls="--")
ax1.set_axisbelow(True)
#
# plt.show()

fig_02 = plt.figure(2, [10, 6])
fig_02.clf()

ax2 = fig_02.add_subplot(1, 1, 1, aspect="equal")

r = Rectangle(
    (39.6, 24.4), 0.2, 0.2, color=(0.5, 0.5, 0.5), alpha=0.75, angle=30, zorder=0
)
ax2.add_patch(r)

# m_list = []
# m_label = []
c_max = np.nanmax(np.abs(delta_rms[np.nonzero(delta_rms)]))
for ii, s_arr in enumerate(r1.residual_array):

    s_max = np.nanmax(delta_rms[ii][8:])
    s_min = np.nanmin(delta_rms[ii][8:])
    if abs(s_min) > abs(s_max):
        s_rms = s_min
    else:
        s_rms = s_max
    if abs(s_rms) < 0.05:
        s_rms = 0.0

    s_rms = np.nanmean(delta_rms[ii][12:])

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
    m1 = ax2.scatter(s_arr["lon"], s_arr["lat"], marker="o", s=350, c=line_color)
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
    )

# ax2.legend(m_list, m_label, loc='lower left', ncol=2)
ax2.set_xlabel("longitude (deg)", fontdict={"size": fs, "weight": "bold"})
ax2.set_ylabel("latitude (deg)", fontdict={"size": fs, "weight": "bold"})
ax2.grid(which="both", color=(0.5, 0.5, 0.5), ls="--")
ax2.set_axisbelow(True)
# ax2.xaxis.set_major_locator(MultipleLocator(.02))
# ax2.yaxis.set_major_locator(MultipleLocator(.02))

# ax2.set_xlim((-107.225, -107.325))
# ax2.set_ylim((33.10, 33.25))

fig.savefig(res_fn_02[0:-4] + "_responses_m.png", dpi=600)
fig_02.savefig(res_fn_02[0:-4] + "_map_m.png", dpi=600)

plt.show()
