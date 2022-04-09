# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 16:06:21 2019

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def archies(sigma_measured, porosity, saturation, n=2, m=2, alpha=1):
    """
    modified archies law
    """

    sigma_w = (sigma_measured * alpha * saturation ** n) / porosity ** m

    return sigma_w


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
    hashin-shtrickman lowe r bound

    sigma_1 is the resistivity of the host material
    sigma_2 is the resistivity of the filling material
    percent_2 is the percentage of the filling material
    """

    s1 = sigma_1
    s2 = sigma_2
    p2 = 1 - percent_2

    sigma_eff = s1 * (1 + (3 * p2 * (s2 - s1)) / (3 * s1 + (1 - p2) * (s2 - s1)))

    return sigma_eff


def sigma_fluid(sigma_zero, initial_temperature, salinty, temperature):
    """ """
    sigma_f = (sigma_zero * (initial_temperature + 21.5)) / (temperature + 21.5)

    return sigma_f


def glover(
    sigma_1, phi_1, m_1, sigma_2, phi_2, m_2, sigma_3=None, phi_3=None, m_3=None
):
    sigma_eff = sigma_1 * phi_1 ** m_1 + sigma_2 * phi_2 ** m_2
    if sigma_3 is not None:
        sigma_eff += sigma_3 * phi_3 ** m_3

    return sigma_eff


# =============================================================================
# Plot different things
# =============================================================================
sigma_gw = 1.0 / 70
phi_3 = 0.04
m_3 = 3
sigma_3 = 100
# saturation = np.linspace(phi_3, 1, 25)
phi_2 = 0.9
sigma_steam = np.logspace(-2, -6, 30)


fig = plt.figure(2)
fig.clf()

ax = fig.add_subplot(1, 1, 1)
labels = []
lines = []
for m_2 in np.arange(0, 4, 0.4, dtype=np.float):
    (l1,) = ax.loglog(
        1.0 / sigma_steam,
        1.0
        / glover(
            1.0 / 70, 1 - phi_2 - phi_3, 1, sigma_steam, phi_2, m_2, sigma_3, phi_3, m_3
        ),
    )
    #    l1, = ax.semilogy(saturation, 1./modified_archies(sigma_steam, sigma_gw, saturation))
    lines.append(l1)
    labels.append("{0:.2f}".format(m_2))

# ax.fill_between([1./sigma_steam.max(), 1./sigma_steam.min()],
#               [50, 50], [100, 100],
#                color=(.75, .75, .75),
#                alpha=.35)

ax.legend(lines, labels)
# ax.xaxis.set_major_locator(MultipleLocator(.1))
ax.set_xlabel("Rho_steam")
ax.set_ylabel("Rho_measured")
ax.grid(which="both", color=(0.5, 0.5, 0.5))

fig.show()
