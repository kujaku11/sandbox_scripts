# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 14:05:35 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
from mtpy.modeling import StructuredGrid3D
from mtpy.core import MTLocation

# =============================================================================
# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2021\gz_2021_z03_c02_048.rho"
# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2022\gz_2022_z03_c02_132.rho"
# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2023\gz_2023_z03_c02_103.rho"
# mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\gz_joint_2023_z03_c02_NLCG_108.rho"
mfn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\gz_joint_2021_z03_c02_NLCG_057.rho"

m2ft = 3.2808399
pad = 7
pad_z = 5
fn_stem = "gz_2021_joint"

model_center = MTLocation(
    latitude=38.812566, longitude=-122.796391, elevation=1150.00
)

# UTM WGS84 Zone 10
model_center.utm_crs = 32610

# UTM CA state map NAD27 zone 2
model_center.utm_crs = 26742

sg = StructuredGrid3D()
sg.from_modem(mfn)


# --> write model xyz file
lines = [
    "# model.type = electrical resistivity",
    "# model.units = log10(Ohm-m)",
    "# model.coordinate_system = right hand with z+ down",
    "# model.name = CEC Geysers Project, Phase 1 larger grid",
    "# model.author = J Peacock",
    "# model.author.organization = U.S. Geological Survey",
    "# model.date = 2023-09-20",
    f"# model.center.latitude = {model_center.latitude}",
    f"# model.center.longitude = {model_center.longitude}",
    f"# model.center.elevation = {model_center.elevation}",
    "# model.center.elevation.units = m",
    f"# model.center.datum = {model_center.datum_name}",
    f"# model.center.datum_epsg = {model_center.datum_epsg}",
    f"# model.center.easting = {model_center.east}",
    f"# model.center.northing = {model_center.north}",
    f"# model.center.utm_datum = {model_center.utm_name}",
    f"# model.center.utm_epsg = {model_center.utm_epsg}",
    "# model.center.utm.units = feet",
    "# model.software = ModEM",
    "# model.starting_lambda = 1000.00",
    "# model.starting_model = 50 ohm-m half-space",
    "# model.rms = 1.9",
    "# model.covariance = 0.02",
    "# data.error.z = 0.03 * sqrt(Zxy * Zyx) floor",
]
lines.append("#north, east, depth, resistivity")

utm_east = sg.grid_east[pad:-pad] * m2ft + model_center.east
utm_north = sg.grid_north[pad:-pad] * m2ft + model_center.north
for kk, zz in enumerate(sg.grid_z[0:-pad_z]):
    for jj, yy in enumerate(utm_east, pad):
        for ii, xx in enumerate(utm_north, pad):
            lines.append(
                f"{xx:.1f},{yy:.1f},{zz:.1f},{np.log10(sg.res_model[ii, jj, kk]):.2f}"
            )

save_fn = sg.save_path.joinpath(
    f"{fn_stem}_resistivity_casp_nad27_zone_2_ft.xyz"
)

with open(save_fn, "w") as fid:
    fid.write("\n".join(lines))

print("Wrote file {0}".format(save_fn))
