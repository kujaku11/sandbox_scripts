# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 15:25:26 2016

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import os
import mtpy.utils.gis_tools as gis_tools
import numpy as np

# mfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_final_err05_cov04_NLCG_040.rho"
# dfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_modem_data_ef05.dat"

mfn = r"c:\Users\jpeacock\Google Drive\LV_Geothermal\SI_Peacock_etal2016_D2.rho"

save_root = "lv"
rot_angle = 0.0

# --> read model file
mod_obj = modem.Model()
mod_obj.read_model_file(mfn)

# --> get center position
c_east, c_north = (331570, 4173660)

# --> set padding
east_pad = mod_obj.pad_east + 4
north_pad = mod_obj.pad_north + 4
z_pad = np.where(mod_obj.grid_z > 30000)[0][0]

cos_ang = np.cos(np.deg2rad(rot_angle))
sin_ang = np.sin(np.deg2rad(rot_angle))
rot_matrix = np.matrix(np.array([[cos_ang, sin_ang], [-sin_ang, cos_ang]]))

# --> write model xyz file
lines = ["# north (m) east(m) depth(m) resistivity (Ohm-m)"]
for kk, zz in enumerate(mod_obj.grid_z[0:z_pad]):
    for jj, yy in enumerate(mod_obj.grid_east[east_pad:-east_pad]):
        for ii, xx in enumerate(mod_obj.grid_north[north_pad:-north_pad]):

            n_east = yy + c_east
            n_north = xx + c_north

            # rotate data
            n_coords = np.array([n_east, n_north])
            new_coords = np.array(np.dot(rot_matrix, n_coords))

            lines.append(
                "{0:>12.1f}{1:12.1f}{2:12.1f}{3:12.2f}".format(
                    new_coords[0, 1],
                    new_coords[0, 0],
                    zz,
                    mod_obj.res_model[ii, jj, kk],
                )
            )

save_fn = os.path.join(os.path.dirname(mfn), "{0}_resistivity.xyz".format(save_root))
with open(save_fn, "w") as fid:
    fid.write("\n".join(lines))

print "Wrote file {0}".format(save_fn)
