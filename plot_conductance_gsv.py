# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 18:11:42 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
import numpy as np
from matplotlib import pyplot as plt
from mtpy.modeling import modem
from mtpy.utils import array2raster


dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GraniteSprings\modem_inv\inv_03\gsv_modem_data_z03_t02.dat"
d = modem.Data()
d.read_data_file(dfn)


# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_topo_inv_02\st_z05_t02_c025_126.rho"
# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_sensitivity\st_1d_flat_070.rho"
mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GraniteSprings\modem_inv\inv_03\gsv_z03_t02_c03_137.rho"
# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_06\um_z05_c03_083.rho"
# model_center = (-118.704435 + .03, 45.597757000000001 + .02)

model_center = (-118.927443, 40.227213)

z_dict = {
    "surface": np.array((0, 2000)),
    "middle_crust": np.array((2000, 11000)),
    "lower_crust": np.array((11000, 30000)),
}
pad = 8


m = modem.Model()
m.read_model_file(mfn)
gx, gy = np.meshgrid(m.grid_east, m.grid_north)

fig = plt.figure(1)
fig.clf()

for ii, key in enumerate(["surface", "middle_crust", "lower_crust"]):
    z = z_dict[key]
    index_min = np.where(m.grid_z <= z.min())[0][-1]
    index_max = np.where(m.grid_z >= z.max())[0][0]

    conductance = (1.0 / m.res_model[:, :, index_min:index_max]) * abs(
        m.grid_z[index_min:index_max]
    )
    conductance = conductance.sum(axis=2)

    ax = fig.add_subplot(1, 3, 1 + ii, aspect="equal")
    im = ax.pcolormesh(
        gx,
        gy,
        conductance,
        cmap="gnuplot2",
        vmin=conductance[pad:-pad, pad:-pad].min(),
        vmax=conductance[pad:-pad, pad:-pad].max(),
    )

    ax.scatter(
        d.station_locations.rel_east, d.station_locations.rel_north, marker="v", s=20
    )
    print(conductance[pad:-pad, pad:-pad].min(), conductance[pad:-pad, pad:-pad].max())
    ax.set_xlim((m.grid_east[pad], m.grid_east[-pad]))
    ax.set_ylim((m.grid_north[pad], m.grid_north[-pad]))

    cb = plt.colorbar(im, ax=ax, shrink=0.35)

    array2raster.array2raster(
        r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GraniteSprings\modem_inv\inv_03\1d_conductance_{0}.tif".format(
            key
        ),
        (-119.052319, 40.179765000000003),
        300.0,
        300.0,
        conductance[pad:-pad, pad:-pad],
    )

    # array2raster.array2raster(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_09\conductance_{0}_crust.tiff".format(key),
    #                           model_center,
    #                           166.,
    #                           110.,
    #                           conductance[pad:-pad, pad:-pad])

plt.show()
