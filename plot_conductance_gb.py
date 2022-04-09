# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 18:11:42 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
from pathlib import Path
import numpy as np
from matplotlib import pyplot as plt
from mtpy.modeling import modem
from mtpy.utils import array2raster


dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_01\gb_z03_t02_c02_046.dat"
d = modem.Data()
d.read_data_file(dfn)

# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\canv_01\canv_t03_c04_084.rho"
mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\gb_01\gb_z03_t02_c02_046.rho"
# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_06\um_z05_c03_083.rho"
# model_center = (-118.704435 + .03, 45.597757000000001 + .02)

model_center = (-119.015192, 38.615252)
lower_left = (-124.2937861, 32.5799747)

z_dict = {
    "surface": np.array((2000, 12000)),
    "middle_crust": np.array((12000, 20000)),
    "lower_crust": np.array((17000, 50000)),
    "upper_mantle": np.array((45000, 90000)),
    "mantle": np.array((90000, 200000)),
}
pad = 10


m = modem.Model()
m.read_model_file(mfn)
gx, gy = np.meshgrid(m.grid_east, m.grid_north)

fig = plt.figure(1)
fig.clf()

for ii, key in enumerate(z_dict.keys()):
    z = z_dict[key]
    index_min = np.where(m.grid_z <= z.min())[0][-1]
    index_max = np.where(m.grid_z >= z.max())[0][0]

    conductance = (1.0 / m.res_model[:, :, index_min:index_max]) * abs(
        m.grid_z[index_min:index_max]
    )
    conductance = np.log10(conductance.sum(axis=2))

    ax = fig.add_subplot(1, len(z_dict.keys()), 1 + ii, aspect="equal")
    im = ax.pcolormesh(gx, gy, conductance, cmap="gnuplot2",)
    # vmin=conductance[pad:-pad, pad:-pad].min(),
    # vmax=conductance[pad:-pad, pad:-pad].max())

    ax.scatter(
        d.station_locations.rel_east, d.station_locations.rel_north, marker="v", s=20
    )
    ax.set_xlim((m.grid_east[pad], m.grid_east[-pad]))
    ax.set_ylim((m.grid_north[pad], m.grid_north[-pad]))

    cb = plt.colorbar(im, ax=ax, shrink=0.35)

    array2raster.array2raster(
        Path(m.save_path).joinpath(f"canv_conductance_impedance_{key}.tiff").as_posix(),
        (lower_left[0], lower_left[1]),
        7000.0,
        7000.0,
        conductance[pad:-pad, pad:-pad],
    )

plt.show()
