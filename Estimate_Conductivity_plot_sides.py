# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 13:12:40 2014

@author: jpeacock-pr
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np


def arrhenius(temperature, wtp_h2o, pressure=1):
    """
    melt resistivity of rhyolite from Gaillard [2004]

    """
    R = 8.314  # units are kJ/mol/K
    sigma_0 = -78.9 * np.log(wtp_h2o) + 754
    Ea = -2925 * np.log(wtp_h2o) + 64132

    return sigma_0 * np.exp(-(Ea + 2 * pressure) / (R * temperature))


def dacite_arrhenius(temperature, wtp_h2o, pressure=1):
    """
    melt resistivity of dacite from Laumonier 2014
    """

    a1 = -0.064
    a2 = 5.96
    a3 = 1.06e-5
    a4 = 2.49e-5
    a5 = -6146.0
    a6 = 88440.0
    a7 = 0.176
    a8 = 0.388

    R = 8.314  # units are kJ/mol/K
    sigma_0 = np.exp((a1 * wtp_h2o + a2) * pressure + a3 * wtp_h2o + a4)
    Ea = a5 * wtp_h2o + a6
    delta_v = a7 * wtp_h2o + a8

    return sigma_0 * np.exp(-(Ea + pressure * delta_v) / (R * temperature))


def basalt_arrhenius(temperature, wtp_k2o):
    """
    electrical resistivity from Gaillard [2005]

    """

    a1 = 0.742
    a2 = -0.105
    b1 = 4.742
    b2 = -0.60

    a = a1 + a2 * wtp_k2o
    b = b1 + b2 * wtp_k2o

    return np.exp(a + b / temperature)


def basalt_ni(temperature, wtp_h2o):
    """
    electrical resistivity of basaltic melt from Ni et al., 2011
    """

    sigma_b = np.exp(
        2.172 - (860.82 - 204.46 * np.sqrt(wtp_h2o)) / (temperature - 1146.8)
    )

    return sigma_b


def nernst_einstein(mobility, charge, concentration, temperature, haven):
    """
    nernst-einstein equation for electrical conductivity of melt
    """
    k = 1.3806e-23
    sigma_melt = mobility * charge ** 2 * concentration / (k * temperature * haven)

    return sigma_melt


def modified_brick(sigma_1, sigma_2, percent_2):
    """
    modified brick mising model

    sigma_1 is the resistivity of the host material
    sigma_2 is the resistivity of the filling material
    percent_2 is the percentage of the filling material
    """

    s1 = sigma_1
    s2 = sigma_2
    p1 = percent_2
    n = 2.0 / 3

    sigma_eff = s2 * (s2 * (p1 ** n - 1) - s1 * p1 ** n) / s1 * (p1 - p1 ** n) - s2 * (
        p1 ** n - p1 - 1
    )

    sigma_eff = np.nan_to_num(sigma_eff)

    return sigma_eff


def modified_archies(sigma_1, sigma_2, percent_2, m=1.05):
    """
    modified archies law

    sigma_1 is the resistivity of the host material
    sigma_2 is the resistivity of the filling material
    percent_2 is the percentage of the filling material
    """
    s1 = sigma_1
    s2 = sigma_2
    p2 = 1 - percent_2

    p = np.log(1 - p2 ** m) / np.log(1 - p2)

    sigma_eff = s1 * (1 - p2) ** p + s2 * p2 ** m

    return sigma_eff


def hs_lower(sigma_1, sigma_2, percent_2):
    """
    hashin-shtrickman lower bound

    sigma_1 is the resistivity of the host material
    sigma_2 is the resistivity of the filling material
    percent_2 is the percentage of the filling material
    """

    s1 = sigma_1
    s2 = sigma_2
    p2 = 1 - percent_2

    sigma_eff = s1 * (1 + (3 * p2 * (s2 - s1)) / (3 * s1 + (1 - p2) * (s2 - s1)))

    return sigma_eff


def viscosity(T, ob, h2o, sigma):
    """
    estimate viscosity from resistivity
    """

    log_nu = 41.09 - 1.5e5 / T + 2.48 * h2o + 139.4 * ob - 31.25 * np.log(sigma)
    nu = np.exp(log_nu)

    return nu


def calculate_ob(concentration_dict):
    """
    calculate optical bacisity using the formulation from Zhang [2010]
    and parameters from Duffy and Ingram [1975], following Pommier, [2013]

    concentration_dict must have keys:
        - ['Al', 'Ca', 'Fe', 'H', 'K', 'Mg', 'Mn', 'Na', 'Si']

    values are percent concentrations for each oxide

    """
    # dictionary of lambda ob values from Duffy
    lob = {
        "K": 1.4,
        "Na": 1.15,
        "Mg": 0.78,
        "Mn": 1.0,
        "Fe": 1.0,
        "Si": 0.48,
        "Al": 0.6,
        "Ca": 1.0,
        "H": 0.47,
    }

    xd = dict(concentration_dict)

    if xd["Ca"] + xd["Mg"] >= xd["Al"]:
        A = (
            2 * lob["Si"] * xd["Si"]
            + 3 * lob["Al"] * xd["Al"]
            + lob["Fe"] * xd["Fe"]
            + lob["Mn"] * xd["Mn"]
            + lob["Mg"] * (xd["Mg"] + xd["Ca"] - xd["Al"])
            + 0.5 * lob["Na"] * xd["Na"]
            + 0.5 * lob["K"] * xd["K"]
            + lob["H"] * xd["H"]
        )

        B = (
            2 ** xd["Si"]
            + 3 * xd["Al"]
            + xd["Fe"]
            + xd["Mn"]
            + (xd["Mg"] + xd["Ca"] - xd["Al"])
            + 0.5 * xd["Na"]
            + 0.5 * xd["K"]
            + xd["H"]
        )

    elif xd["Ca"] + xd["Mg"] < xd["Al"]:
        A = (
            2 * lob["Si"] * xd["Si"]
            + 3 * lob["Al"] * xd["Al"]
            + lob["Fe"] * xd["Fe"]
            + lob["Mn"] * xd["Mn"]
            + lob["Mg"] * xd["Mg"]
            + lob["Ca"] * xd["Ca"]
            + 0.5 * lob["Na"] * xd["Na"]
            + 0.5 * lob["K"] * xd["K"]
            + lob["H"] * xd["H"]
        )

        B = (
            2 ** xd["Si"]
            + 3 * xd["Al"]
            + xd["Fe"]
            + xd["Mn"]
            + xd["Mg"]
            + xd["Ca"]
            + 0.5 * xd["Na"]
            + 0.5 * xd["K"]
            + xd["H"]
        )

    return A / B


# ==============================================================================
# input values
# ==============================================================================
T = np.arange(725, 1200, step=20) + 273.5  # temperature array
T_basalt = np.arange(1000, 1600, step=20) + 273.5  # temperature array
T_r = 825.0 + 273.5  # rhyolite temperature
T_d = 900.0 + 273.5  # dacite temperature
T_b = 1400.0 + 273.5  # dacite temperature


melt_percent = np.arange(0, 51, 5) / 100.0  # melt percent array

sigma_regional = 1.0 / 100

ob_rhyolite_dict = {
    "K": 0.047,
    "Na": 0.038,
    "Mg": 0.0001,
    "Mn": 0.0006,
    "Fe": 0.012,
    "Si": 0.75,
    "Al": 0.123,
    "Ca": 0.005,
    "H": 0.03,
}
ob_dacite_dict = {
    "K": 0.04,
    "Na": 0.04,
    "Mg": 0.0007,
    "Mn": 0.01,
    "Fe": 0.023,
    "Si": 0.63,
    "Al": 0.16,
    "Ca": 0.03,
    "H": 0.03,
}

ob_rhyolite = 1 - calculate_ob(ob_rhyolite_dict)
ob_dacite = 1 - calculate_ob(ob_dacite_dict)

wtp_h2o_min = 1.0
wtp_h2o_max = 5.0

marker_size = 3

# ==============================================================================
# plot just mixing relations
# ==============================================================================
plt.close("all")
plt.rcParams["font.size"] = 9
plt.rcParams["figure.subplot.hspace"] = 0.3
plt.rcParams["figure.subplot.top"] = 0.9
plt.rcParams["figure.subplot.bottom"] = 0.14
plt.rcParams["figure.subplot.left"] = 0.12
plt.rcParams["figure.subplot.right"] = 0.97
plt.rcParams["figure.subplot.wspace"] = 0.25
plt.rcParams["grid.linewidth"] = 0.15
plt.rcParams["grid.color"] = (0.5, 0.5, 0.5)

label_font_dict = {"size": 10, "weight": "bold"}
ylabel_coords = (-0.135, 0.5)
xlabel_coords = (0.5, -0.125)

fig = plt.figure(1, figsize=[4, 4], dpi=300)
ax = fig.add_subplot(1, 1, 1)

plt.cla()
line_list = []
label_list = []

line_list2 = []
label_list2 = []

line_list3 = []
label_list3 = []

line_list_mp = []
label_list_mp = []

for wtp_h2o in np.arange(wtp_h2o_min, wtp_h2o_max + 1, 1.0):
    if wtp_h2o == 0:
        wtp_h2o = 0.01

    # --> plot resistivity vs. temperature
    line_color = tuple(3 * [0.9 - 0.9 * wtp_h2o / (wtp_h2o_max)])
    #    line_color = (0, 0, wtp_h2o/(wtp_h2o_max))
    sigma_a = arrhenius(T, wtp_h2o, pressure=0.5)

    sigma_d = dacite_arrhenius(T, wtp_h2o, pressure=1.2)

    ## basalt
    sigma_b = basalt_ni(T_basalt, wtp_h2o)

    ##--> plot melt percentage vs. bulk resistivity
    sigma_melt = arrhenius(T_r, wtp_h2o)
    sigma_ma_low = modified_archies(sigma_regional, sigma_melt, 1 - melt_percent)
    sigma_ma_low[0] = sigma_regional

    (line_rhyolite,) = ax.semilogx(
        1.0 / sigma_ma_low,
        melt_percent,
        "-",
        lw=0.5,
        marker="s",
        ms=marker_size,
        mec=line_color,
        color=line_color,
    )

    sigma_melt = dacite_arrhenius(T_d, wtp_h2o)
    sigma_ma_low = modified_archies(sigma_regional, sigma_melt, 1 - melt_percent)
    sigma_ma_low[0] = sigma_regional

    (line_dacite,) = ax.semilogx(
        1.0 / sigma_ma_low,
        melt_percent,
        "-.",
        lw=0.5,
        marker="o",
        ms=marker_size,
        mec=line_color,
        color=line_color,
    )
    line_dacite.set_dashes((3, 1))

    sigma_melt = basalt_ni(T_b, wtp_h2o)
    sigma_ma_low = modified_archies(sigma_regional, sigma_melt, 1 - melt_percent)
    sigma_ma_low[0] = sigma_regional

    (line_basalt,) = ax.semilogx(
        1.0 / sigma_ma_low,
        melt_percent,
        "-.",
        lw=0.5,
        marker="*",
        ms=marker_size,
        mec=line_color,
        color=line_color,
    )
    line_basalt.set_dashes((3, 1))

    if wtp_h2o == wtp_h2o_max:

        # --> line list for melt resistivity vs. temperature
        line_list2.append(line_rhyolite)
        label_list2.append("rhyolite")
        line_list2.append(line_dacite)
        label_list2.append("dacite")
        line_list2.append(line_basalt)
        label_list2.append("basalt")
    #

    line_list.append(line_rhyolite)
    label_list.append(" {0:.0f}% $H_2O$".format(wtp_h2o))


# make a legend on top of the figure for water percent
fig.legend(
    line_list,
    label_list,
    loc="upper center",
    prop={"size": 8},
    ncol=5,
    markerscale=0.5,
    handletextpad=0.05,
    columnspacing=0.05,
)


##--> resistivity vs. melt percent
ax.fill_between([5, 15], [0, 0], [0.5, 0.5], color=(0.75, 0.75, 0.75), alpha=0.35)

ax.set_ylabel("Melt Percent", fontdict=label_font_dict)
ax.set_xlabel("Bulk Resistivity ($\Omega \cdot$m)", fontdict=label_font_dict)
ax.set_ylim(0, 0.5)
ax.set_xlim(2, 1 / sigma_regional)
ax.yaxis.set_minor_locator(MultipleLocator(0.05))
ax.yaxis.grid(which="both")
ax.xaxis.grid(which="both")
ax.legend(line_list2, label_list2, loc="upper right", prop={"size": 8}, ncol=1)

fig.savefig(
    r"c:\Users\jpeacock-pr\Documents\TexDocs\Figures\melt_percent_plot.pdf", dpi=600
)
##==============================================================================
##  plot only melt resistivity
##==============================================================================
# plt.close('all')
# plt.rcParams['font.size'] = 9
# plt.rcParams['figure.subplot.hspace'] = .3
# plt.rcParams['figure.subplot.top'] = .9
# plt.rcParams['figure.subplot.bottom'] = .14
# plt.rcParams['figure.subplot.left'] = .13
# plt.rcParams['figure.subplot.right'] = .95
# plt.rcParams['figure.subplot.wspace'] = .25
# plt.rcParams['grid.linewidth'] = .15
# plt.rcParams['grid.color'] = (.5, .5, .5)
#
# label_font_dict = {'size':10, 'weight':'bold'}
# ylabel_coords = (-.135, .5)
# xlabel_coords = (.5, -.125)
#
# fig = plt.figure(1, figsize=[4, 4], dpi=300)
# ax = fig.add_subplot(1, 1, 1)
#
# plt.cla()
# line_list = []
# label_list = []
#
# line_list2 = []
# label_list2 = []
#
# line_list3 = []
# label_list3 = []
#
# line_list_mp = []
# label_list_mp = []
#
# for wtp_h2o in np.arange(wtp_h2o_min, wtp_h2o_max+1, 1.0):
#    if wtp_h2o == 0:
#        wtp_h2o = .01
#
#    #--> plot resistivity vs. temperature
#    line_color = tuple(3*[.9-.9*wtp_h2o/(wtp_h2o_max)])
##    line_color = (0, 0, wtp_h2o/(wtp_h2o_max))
#    sigma_a = arrhenius(T, wtp_h2o, pressure=.5)
#    line_rhyolite, = ax.semilogy(T-273.5, 1./sigma_a,
#                      '-',
#                      marker='s',
#                      ms=3,
#                      lw=.5,
#                      color=line_color,
#                      mfc=line_color,
#                      mec=line_color)
#
#    sigma_d = dacite_arrhenius(T, wtp_h2o, pressure=1.2)
#    if wtp_h2o < 5:
#        line_dacite, = ax.semilogy(T-273.5, 1./sigma_d,
#                          '-.',
#                          marker='o',
#                          ms=3,
#                          lw=.5,
#                          color=line_color,
#                          mfc=line_color,
#                          mec=line_color)
#        line_dacite.set_dashes((3,1))
#
#    ## basalt
#    sigma_b = basalt_ni(T_basalt, wtp_h2o)
#
#    line_basalt, = ax.semilogy(T_basalt-273.5,
#                             1./sigma_b,
#                      '--',
#                      marker='*',
#                      ms=3,
#                      lw=.5,
#                      color=line_color,
#                      mfc=line_color,
#                      mec=line_color)
#    line_basalt.set_dashes((3,1))
#    if wtp_h2o == wtp_h2o_max:
#        #--> line list for melt resistivity vs. temperature
#        line_list2.append(line_rhyolite)
#        label_list2.append('rhyolite')
#        line_list2.append(line_dacite)
#        label_list2.append('dacite')
#        line_list2.append(line_basalt)
#        label_list2.append('basalt')
#
#    line_list.append(line_rhyolite)
#    label_list.append(' {0:.0f}% $H_2O$'.format(wtp_h2o))
#
##make a legend on top of the figure for water percent
# fig.legend(line_list, label_list,
#           loc='upper center',
#           prop={'size':8},
#           ncol=5,
#           markerscale=.5,
#           handletextpad=.05,
#           columnspacing=.05)
#
##--> resitivity vs temperature
# ax.fill_between([720, 850], [.01, .01], [500, 500],
#                color=(.75, .75, .75),
#                alpha=.35)
# ax.set_xlabel('Temperature ($^\circ$C)',
#               fontdict=label_font_dict)
# ax.set_ylabel('Melt Resistivity ($\Omega \cdot$m)',
#               fontdict=label_font_dict)
# ax.legend(line_list2, label_list2, loc='upper right', prop={'size':8},
#          ncol=1)
# ax.grid(which='both')
# ax.set_ylim(.2, 10)
# ax.set_xlim(700, 1599)
#
# fig.savefig(r"c:\Users\jpeacock-pr\Documents\TexDocs\Figures\melt_resistivities_plot.pdf",
#            dpi=300)
#
#
# ==============================================================================
#     melt percent vs host rock
# ==============================================================================
# ==============================================================================
# plot just mixing relations
# ==============================================================================
plt.close("all")
plt.rcParams["font.size"] = 9
plt.rcParams["figure.subplot.hspace"] = 0.3
plt.rcParams["figure.subplot.top"] = 0.9
plt.rcParams["figure.subplot.bottom"] = 0.14
plt.rcParams["figure.subplot.left"] = 0.14
plt.rcParams["figure.subplot.right"] = 0.97
plt.rcParams["figure.subplot.wspace"] = 0.25
plt.rcParams["grid.linewidth"] = 0.15
plt.rcParams["grid.color"] = (0.5, 0.5, 0.5)

label_font_dict = {"size": 10, "weight": "bold"}
ylabel_coords = (-0.135, 0.5)
xlabel_coords = (0.5, -0.125)

# fig = plt.figure(1, figsize=[3, 4], dpi=300)
fig = plt.figure(1, figsize=[4, 4], dpi=300)
ax = fig.add_subplot(1, 1, 1)
# ax2 = fig.add_subplot(3, 1, 2)
# ax3 = fig.add_subplot(1, 2, 2)

plt.cla()
line_list = []
label_list = []

line_list2 = []
label_list2 = []

line_list3 = []
label_list3 = []

line_list_mp = []
label_list_mp = []

for host_rock in [50, 100, 500, 1000, 10000]:
    # --> plot resistivity vs. temperature
    line_color = tuple(3 * [1 - 0.9 * np.log10(host_rock) / (4.0)])
    #    line_color = (0, 0, wtp_h2o/(wtp_h2o_max))
    sigma_a = arrhenius(T, 2, pressure=0.5)

    sigma_d = dacite_arrhenius(T, 2, pressure=1.2)

    ## basalt
    sigma_b = basalt_ni(T_basalt, 2)

    ##--> plot melt percentage vs. bulk resistivity
    sigma_melt = arrhenius(T_r, 2)
    sigma_ma_low = modified_archies(1.0 / host_rock, sigma_melt, 1 - melt_percent)
    sigma_ma_low[0] = 1.0 / host_rock

    (line_rhyolite,) = ax.semilogx(
        1.0 / sigma_ma_low,
        melt_percent,
        "-",
        lw=0.5,
        marker="s",
        ms=marker_size,
        mec=line_color,
        color=line_color,
    )

    sigma_melt = dacite_arrhenius(T_d, 2)
    sigma_ma_low = modified_archies(1.0 / host_rock, sigma_melt, 1 - melt_percent)
    sigma_ma_low[0] = 1.0 / host_rock

    (line_dacite,) = ax.semilogx(
        1.0 / sigma_ma_low,
        melt_percent,
        "-.",
        lw=0.5,
        marker="o",
        ms=marker_size,
        mec=line_color,
        color=line_color,
    )
    line_dacite.set_dashes((3, 1))

    sigma_melt = basalt_ni(T_b, 2)
    sigma_ma_low = modified_archies(1.0 / host_rock, sigma_melt, 1 - melt_percent)
    sigma_ma_low[0] = 1.0 / host_rock

    (line_basalt,) = ax.semilogx(
        1.0 / sigma_ma_low,
        melt_percent,
        "-.",
        lw=0.5,
        marker="*",
        ms=marker_size,
        mec=line_color,
        color=line_color,
    )
    line_basalt.set_dashes((3, 1))

    if host_rock == 10000:
        # --> line list for viscosity
        #        line_list3.append(line_nu_rhyolite)
        #        label_list3.append('rhyolite')
        #        line_list3.append(line_nu_dacite)
        #        label_list3.append('dacite')

        # --> line list for melt resistivity vs. temperature
        line_list2.append(line_rhyolite)
        label_list2.append("rhyolite")
        line_list2.append(line_dacite)
        label_list2.append("dacite")
        line_list2.append(line_basalt)
        label_list2.append("basalt")
    #

    line_list.append(line_rhyolite)
    label_list.append(" {0:.0f} $\Omega \cdot m$".format(host_rock))


# make a legend on top of the figure for water percent
fig.legend(
    line_list,
    label_list,
    loc="upper center",
    prop={"size": 8},
    ncol=5,
    markerscale=0.5,
    handletextpad=0.05,
    columnspacing=0.05,
)


##--> resistivity vs. melt percent
ax.fill_between([5, 15], [0, 0], [0.5, 0.5], color=(0.75, 0.75, 0.75), alpha=0.35)

ax.set_ylabel("Melt Percent", fontdict=label_font_dict)
ax.set_xlabel("Bulk Resistivity ($\Omega \cdot$m)", fontdict=label_font_dict)
ax.set_ylim(0, 0.2)
ax.set_xlim(2, 10000)
ax.yaxis.set_minor_locator(MultipleLocator(0.05))
ax.yaxis.grid(which="both")
ax.xaxis.grid(which="both")
ax.legend(line_list2, label_list2, loc="upper right", prop={"size": 8}, ncol=1)

fig.savefig(
    r"c:\Users\jpeacock-pr\Documents\TexDocs\Figures\melt_percent_plot_02.pdf", dpi=600
)
