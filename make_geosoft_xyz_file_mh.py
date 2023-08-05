# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 15:25:26 2016

@author: jpeacock
"""

import mtpy.modeling.modem as modem
import os
import mtpy.utils.gis_tools as gis_tools
import numpy as np
import matplotlib.pyplot as plt

mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\MountainHome\modem_inv\inv_01\mh_z05_t03_c03_100.rho"
dfn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\MountainHome\modem_inv\inv_01\mh_modem_data_ef05_tip03.dat"

save_root = "mh"
rot_angle = 0.0

# --> read model file
mod_obj = modem.Model()
mod_obj.read_model_file(mfn)

# --> get center position
model_center = (43.056413, -115.892029)
c_east, c_north, c_zone = gis_tools.project_point_ll2utm(
    model_center[0], model_center[1], epsg=26911
)


# --> set padding
east_pad = 7
north_pad = 7
z_pad = np.where(mod_obj.grid_z > 50000)[0][0]

cos_ang = np.cos(np.deg2rad(rot_angle))
sin_ang = np.sin(np.deg2rad(rot_angle))
rot_matrix = np.matrix(np.array([[cos_ang, sin_ang], [-sin_ang, cos_ang]]))

# --> write model xyz file
lines = [
    "# model_type = electrical resistivity",
    "# model_location = Mountain Home, ID",
    "# model_author = J Peacock",
    "# model_organization = U.S. Geological Survey",
    "# model_date = 2018-12-11",
    "# model_datum = NAD83 / UTM Zone 11",
    "# model_program = ModEM",
    "# model_starting_lambda = 100.00",
    "# model_starting_model = 100 ohm-m half-space",
    "# model_rms = 1.2",
    "# data_error_z = 0.05 * sqrt(Zxy * Zyx) floor",
    "# data_error_t = 0.02 floor",
    "# covariance = 0.03",
]
lines.append("# north (m) east(m) depth(m) resistivity (Ohm-m)")

utm_east = mod_obj.grid_east[east_pad:-east_pad] + c_east
utm_north = mod_obj.grid_north[north_pad:-north_pad] + c_north
for kk, zz in enumerate(mod_obj.grid_z[0:z_pad]):
    for jj, yy in enumerate(utm_east, east_pad):
        for ii, xx in enumerate(utm_north, north_pad):

            n_east = yy
            n_north = xx

            # rotate data
            n_coords = np.array([n_east, n_north])
            new_coords = np.array(np.dot(rot_matrix, n_coords))

            #            lines.append('{0:>12.1f}{1:12.1f}{2:12.1f}{3:12.2f}'.format(
            #                          new_coords[0, 1],
            #                          new_coords[0, 0],
            #                          zz,
            #                          mod_obj.res_model[ii, jj, kk]))
            lines.append(
                "{0:.1f},{1:.1f},{2:.1f},{3:.2f}".format(
                    new_coords[0, 1],
                    new_coords[0, 0],
                    zz,
                    mod_obj.res_model[ii, jj, kk],
                )
            )

save_fn = os.path.join(
    os.path.dirname(mfn), "{0}_resistivity_nad83_utm_11.xyz".format(save_root)
)
with open(save_fn, "w") as fid:
    fid.write("\n".join(lines))

print("Wrote file {0}".format(save_fn))


## test to make sure its properly oriented

d_obj = modem.Data()
d_obj.read_data_file(dfn)

# write data coordinates in model coordinates
d_list = ["station,east,north"]
stations_east = []
stations_north = []
for d_arr in d_obj.data_array:
    s_east, s_north, s_zone = gis_tools.project_point_ll2utm(
        d_arr["lat"], d_arr["lon"], epsg=26911
    )
    stations_east.append(s_east)
    stations_north.append(s_north)
    d_list.append(
        "{0},{1:.2f},{2:.2f}".format(d_arr["station"], s_east, s_north)
    )

with open(save_fn[:-4] + "_stations.csv", "w") as fid:
    fid.write("\n".join(d_list))


plot_x, plot_y = np.meshgrid(utm_east, utm_north)
fig = plt.figure(3)
fig.clf()
ax = fig.add_subplot(1, 1, 1, aspect="equal")
im = ax.pcolormesh(
    plot_x,
    plot_y,
    np.log10(mod_obj.res_model[north_pad:-north_pad, east_pad:-east_pad, 4]),
    cmap="jet_r",
    vmin=0,
    vmax=2.5,
)
cb = plt.colorbar(im, ax=ax)

ax.scatter(stations_east, stations_north, marker="v", c="k", s=25)
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")

plt.show()
