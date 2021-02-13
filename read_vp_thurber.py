# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 12:20:58 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
from pathlib import Path
import numpy as np
from scipy.interpolate import griddata
from pyevtk.hl import gridToVTK
from mtpy.utils import gis_tools

fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\earth_models\NCAL_dep.vel.7-1")
vtk_fn = Path(fn.parent, fn.stem)
model_utm_zone = "10S"

east = []
north = []
z = []
vp = []
entries = []
with open(fn, "r") as fid:
    lines = fid.readlines()

for line in lines:
    if "depth" in line:
        z.append(float(line.strip().split()[2]))
        depth = z[-1]
    else:
        lat, lon, value = [float(vv) for vv in line.strip().split()]
        ve, vn, vg = gis_tools.project_point_ll2utm(lat, lon, utm_zone=model_utm_zone)
        entries.append((lat, lon, vn, ve, depth, value))
        
# make the entries into an np array for easier use.    
entries = np.array(entries, dtype=[
    ("lat", np.float),
    ("lon", np.float),
    ("north", np.float),
    ("east", np.float),
    ("depth", np.float),
    ("vp", np.float)])

# get all unique cell locations
grid_east = np.unique(entries["east"])
grid_north = np.unique(entries["north"])
grid_z = np.unique(entries["depth"])
vp = np.zeros((grid_east.size, grid_north.size, grid_z.size))


ge, gn = np.meshgrid(grid_east, grid_north)
xi = np.vstack([arr.flatten() for arr in [ge, gn]]).T
for ii, zz in enumerate(grid_z):
    level = entries[np.where(entries["depth"] == zz)]
    points = np.vstack([arr.flatten() for arr in [level["east"], level["north"]]]).T
    values = level["vp"].flatten()
    
    vp[:, :, ii] = griddata(points, values, xi, method="linear").reshape(ge.shape)
    
# need to add an extra cell to each direction for vtk all in meters.
vtk_east = np.append(grid_east, grid_east[-1] * 1.001)
vtk_north = np.append(grid_north, grid_north[-1] * 1.001)
vtk_z = np.append(np.array([0]), grid_z) * 1000

# write VTK file
gridToVTK(vtk_fn.as_posix(), vtk_north, vtk_east, vtk_z, cellData={"Vp": vp})


