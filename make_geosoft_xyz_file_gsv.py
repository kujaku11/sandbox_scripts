# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 15:25:26 2016

@author: jpeacock
"""

from pathlib import Path
import mtpy.modeling.modem as modem

import numpy as np
import matplotlib.pyplot as plt

mfn = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GraniteSprings\modem_inv\inv_03\gsv_z03_t02_c03_137.rho")
dfn = Path(r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GraniteSprings\modem_inv\inv_03\gsv_modem_data_z03_t02.dat")
save_root = "gsv"
rot_angle = 0.0

# --> read model file
mod_obj = modem.Model()
mod_obj.read_model_file(mfn)

data_obj = modem.Data()
data_obj.read_data_file(dfn)

c_east = data_obj.center_point.east[0] + 600
c_north = data_obj.center_point.north[0] + 8200

# --> get center position
# model_center = (40.2257922, -118.924755)
# # model_center = (38.772697, -118.149196)
# c_east, c_north, c_zone = gis_tools.project_point_ll2utm(
#     model_center[0], model_center[1], "WGS84"
# )


# --> set padding
east_pad = 8
north_pad = 8
z_pad = np.where(mod_obj.grid_z > 10000)[0][0]

cos_ang = np.cos(np.deg2rad(rot_angle))
sin_ang = np.sin(np.deg2rad(rot_angle))
rot_matrix = np.matrix(np.array([[cos_ang, sin_ang], [-sin_ang, cos_ang]]))

# --> write model xyz file
lines = [
    "# model_type = electrical resistivity",
    "# model_location = Granite Springs, NV",
    "# model_author = J Peacock",
    "# model_organization = U.S. Geological Survey",
    "# model_date = 2017-12-10",
    "# model_datum = NAD83 / UTM Zone 11",
    "# model_program = ModEM",
    "# model_starting_lambda = 30.00",
    "# model_starting_model = 100 ohm-m half-space",
    "# model_prior_model = gv_t03_c03_NLCG_031.prm",
    "# model_rms = 2.6",
    "# data_error_z = 0.03 * sqrt(Zxy * Zyx) floor",
    "# data_error_t = 0.03 floor",
    "# covariance = 0.02 applied twice",
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

save_fn = mfn.parent.joinpath(f"{save_root}_resistivity_wgs84.xyz")

with open(save_fn, "w") as fid:
    fid.write("\n".join(lines))

print(f"Wrote file {mfn}")

## test to make sure its properly oriented


# write data coordinates in model coordinates
d_list = ["station,east, north"]
for d_arr in data_obj.data_array:
    d_list.append(
        "{0},{1:.2f},{2:.2f}".format(d_arr["station"], d_arr["east"], d_arr["north"])
    )
with open(save_fn.parent.joinpath(f"{save_root}_stations.csv"), "w") as fid:
    fid.write("\n".join(d_list))


plot_x, plot_y = np.meshgrid(utm_east, utm_north)
fig = plt.figure(1)
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

ax.scatter(
    data_obj.station_locations.east, data_obj.station_locations.north, marker="v", c="k", s=25
)
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")

plt.show()
