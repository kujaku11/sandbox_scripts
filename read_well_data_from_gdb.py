# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 16:14:10 2020

:author: Jared Peacock

:license: MIT

"""

import geopandas as gpd
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator

g = gpd.read_file(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\gis\Umatilla_2020\Umatilla_2020.gdb"
)

# feet to meters
f = 0.3048
width = 10
colors = {
    "basalt": (101 / 256, 80 / 256, 37 / 256),
    "water": (55 / 256, 135 / 256, 205 / 256),
    "brown": (101 / 256, 80 / 256, 37 / 256),
    "black": (0, 0, 0),
    "lightbrown": (191 / 256, 145 / 256, 55 / 256),
    "gray": (0.5, 0.5, 0.5),
    "green": (7 / 256, 115 / 256, 29 / 256),
    "dark brown": (63 / 256, 48 / 256, 0),
    "soil": (210 / 256, 117 / 256, 68 / 256),
    "red": (0.85, 0.1, 0),
    "blue": (0.05, 0.1, 0.85),
}

# Area 1: straughan well 2, area 1, 1856, 1008, 765, 1837 769, 770, 772
# area 3: 783, 781, 782, 774, 575, 1845, 572
# area 1: 809, 807, 808, 905, 806, 795, 799, 791
# well_id = 783

for well_id in [774]:
    well = g[g.SiteID == well_id]

    fig = plt.figure(1, [5.5, 8.5])
    fig.clf()

    ax = fig.add_subplot(1, 1, 1, aspect="equal")

    for index, level in well.iterrows():
        fill = (0.5, 0.5, 0.5)
        materials = level.Material
        # materials = [ss.strip() for ss in level.Material.split(',')]
        # if materials[0] == 'basalt' and len(materials) > 1:
        #     materials = materials[1:]
        if "water bearing" in materials:
            fill = colors["water"]
        else:
            for k, v in colors.items():
                if k in materials:
                    fill = v
                    # break

        ax.fill_between(
            [0, width], [level.From_Elev * f] * 2, [level.To_Elev * f] * 2, color=fill
        )
        ax.text(
            width * 1.2,
            sum([level.From_Elev * f, level.To_Elev * f]) / 2,
            level.Material,
            va="baseline",
            ha="left",
            fontdict={"size": 10},
        )

    ax.set_ylabel("Elevation [m]", fontdict={"size": 16})
    ax.yaxis.set_major_locator(MultipleLocator(width))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    ax.set_title(
        f"Well ID: {int(level.SiteID)}\n{level.Easting}E, {level.Northing}N",
        fontdict={"size": 16, "weight": "bold"},
    )
    fig.tight_layout()

    plt.show()

    fig.savefig(
        r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\Figures\well_id_{0}.png".format(
            well_id
        ),
        dpi=300,
    )
