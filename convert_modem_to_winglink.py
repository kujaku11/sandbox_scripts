# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 13:08:58 2017

@author: jpeacock
"""

import mtpy.modeling.modem as modem

modem_model_fn = (
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\modem_inv\st_topo_inv_02\st_z05_t02_c035_102.rho"
)
wl_fn = modem_model_fn[0:-4] + ".out"


mod_obj = modem.Model()
mod_obj.read_model_file(modem_model_fn)

nx, ny, nz = mod_obj.res_model.shape
n_air = 10
air_res = 1e10

# convert to winglink format

wlk_lines = []

# header line NX, NY, NZ, Nair, Values
wlk_lines.append(
    "{0:>15.0f}{1:>15.0f}{2:>15.0f}{3:>15.0f}{4:>15}".format(
        nx, ny, nz, n_air, "VALUES"
    )
)

# write out north
x_str = ""
for ii, xx in enumerate(mod_obj.nodes_north, 1):
    x_str += "{0:>15.1f}".format(xx)
    if ii % 5 == 0:
        wlk_lines.append(x_str)
        x_str = ""

# write out east
y_str = ""
for ii, yy in enumerate(mod_obj.nodes_east, 1):
    y_str += "{0:>15.1f}".format(yy)
    if ii % 5 == 0:
        wlk_lines.append(y_str)
        y_str = ""

# write out vertical
z_str = ""
for ii, zz in enumerate(mod_obj.nodes_z, 1):
    z_str += "{0:>15.1f}".format(zz)
    if ii % 5 == 0:
        wlk_lines.append(z_str)
        z_str = ""

# write out air layers

for ii in range(1, 11):
    wlk_lines.append("{0:>15.0f}".format(ii))
    count = 0
    x_str = ""
    for jj in range(ny):
        for kk in range(nx):
            x_str += "{0:>15.1E}".format(air_res)
            count += 1
            if count % 5 == 0:
                wlk_lines.append(x_str)
                x_str = ""
    wlk_lines.append(x_str)

# write resistivity values
for ii in range(nz):
    wlk_lines.append("{0:>15.0f}".format(ii + 11))
    count = 0
    x_str = ""
    for jj in range(ny):
        for kk in range(nx):
            x_str += "{0:>15.1f}".format(mod_obj.res_model[kk, jj, ii])
            count += 1
            if count % 5 == 0:
                wlk_lines.append(x_str)
                x_str = ""
    wlk_lines.append(x_str)

wlk_lines.append("WINGLINK")
wlk_lines.append("             1             1  (i j block numbers)")
wlk_lines.append("  396.251217   4303.4740309 (real world coordinates)")
wlk_lines.append("             0  (rotation)")
wlk_lines.append("      -2.461  (top elevation)")
wlk_lines.append("")

# write file
with open(wl_fn, "w") as fid:
    fid.write("\n".join(wlk_lines))
