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

mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_topo_inv_02\st_z05_t02_c025_126.rho"

z_dict = {"surface": np.array((0, 5000)),
          "middle_crust": np.array((5000, 12000)),
          "lower_crust": np.array((12000, 27000))}
pad = 7

m = modem.Model()
m.read_model_file(mfn)
gx, gy = np.meshgrid(m.grid_east, m.grid_north)

fig = plt.figure(1)
fig.clf()

for ii, key in enumerate(["surface", "middle_crust", "lower_crust"]): 
    z = z_dict[key]
    index_min = np.where(m.grid_z <= z.min())[0][-1]
    index_max = np.where(m.grid_z >= z.max())[0][0]
    
    conductance = (1./m.res_model[:, :, index_min:index_max]) * abs(m.grid_z[index_min:index_max])
    conductance = conductance.sum(axis=2)
    
    ax = fig.add_subplot(1, 3, 1 + ii, aspect="equal")
    im = ax.pcolormesh(gx, gy,
                       conductance, 
                       cmap="hot", 
                       vmin=conductance[pad:-pad, pad:-pad].min(),
                       vmax=conductance[pad:-pad, pad:-pad].max())
    
    ax.set_xlim((m.grid_east[pad], m.grid_east[-pad]))
    ax.set_ylim((m.grid_north[pad], m.grid_north[-pad]))
    
    cb = plt.colorbar(im, ax=ax)
    

    
    array2raster.array2raster(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\st_figures\conductance_{0}_crust.tiff".format(key),
                              (-118.590929, 38.541344000000002),
                              750.,
                              750.,
                              conductance[pad:-pad, pad:-pad])
    
plt.show()
