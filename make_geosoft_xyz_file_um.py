# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 15:25:26 2016

@author: jpeacock
"""

import os
import numpy as np
from mtpy.modeling import modem
from mtpy.utils import gis_tools

# mfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_final_err05_cov04_NLCG_040.rho"
# dfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_modem_data_ef05.dat"

mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_09\um_z05_c025_086.rho"
dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\modem_inv\inv_09\um_modem_data_z05_te2.dat"

save_root = "um"

# --> read model file
mod_obj = modem.Model()
mod_obj.read_model_file(mfn)

# --> read data file
d_obj = modem.Data()
d_obj.read_data_file(dfn)

# --> get center position
d_obj.station_locations.calculate_rel_locations()
model_center = d_obj.center_point
c_east, c_north, c_zone = gis_tools.project_point_ll2utm(
    model_center[0].lat, model_center[0].lon, epsg=26911
)

# --> set padding
mod_obj.write_geosoft_xyz(
    mfn[:-4] + "NAD83_11N.xyz",
    c_east=c_east - 750,
    c_north=c_north - 750,
    pad_north=5,
    pad_east=5, 
    pad_z=17,
)

# # --> write model xyz file
# lines = ["nort,east,elevation,resistivity"]
# for kk, zz in enumerate(mod_obj.grid_z[0:z_pad]):
#     for jj, yy in enumerate(mod_obj.grid_east[east_pad:-east_pad]):
#         for ii, xx in enumerate(mod_obj.grid_north[north_pad:-north_pad]):
#             lines.append(f"{xx + c_north},{yy + c_east},{zz},{mod_obj.res_model[ii, jj, kk]}")


# save_fn = os.path.join(os.path.dirname(mfn), "{0}_resistivity.csv".format(save_root))
# with open(save_fn, "w") as fid:
#     fid.write("\n".join(lines))

# print("Wrote file {0}".format(save_fn))
# # --> write data xyz file
# d_lines = ["station,east,north,elevation"]
# for s_arr in d_obj.station_locations.station_locations:
#     d_lines.append(f"{s_arr['station']},{s_arr['east']},{s_arr['north']},{s_arr['elev']}")

# save_fn = os.path.join(os.path.dirname(mfn), "{0}_stations.csv".format(save_root))
# with open(save_fn, "w") as fid:
#     fid.write("\n".join(d_lines))
# print("Wrote file {0}".format(save_fn))
