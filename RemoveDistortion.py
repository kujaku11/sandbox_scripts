# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 14:50:00 2013

@author: jpeacock-pr
"""

# ==============================================================================
import mtpy.core.edi as mtedi
import mtpy.analysis.distortion as distortion
import os

# ==============================================================================

# directory path where edi files are
dirpath = r"d:\Peacock\MTData\EDI_Files\Counts"

# path to save edi files that have distortion removed
drpath = os.path.join(dirpath, "DR")

# make sure the drpath exists
if not os.path.exists(drpath):
    os.mkdir(drpath)

# make a list of all edi files in the directory
edi_list = [
    os.path.join(dirpath, edi) for edi in os.listdir(dirpath) if edi.find(".edi") > 0
]

# loop over edi files and remove distortion
dlst = []
for edi in edi_list:
    e1 = mtedi.Edi(filename=edi)
    d, zd = distortion.remove_distortion(z_object=e1.Z)
    e1.Z = zd
    e1.writefile(os.path.join(dirpath, "DR", e1.station.lower()))
    dlst.append({"station": e1.station, "d": d})

# print results for easy viewing
for dd in dlst:
    print "--> Distortion tensor for {0} is:".format(dd["station"])
    print "{0}|{1: .2f} {2: .2f}|".format("" * 5, dd["d"][0, 0], dd["d"][0, 1])
    print "{0}|{1: .2f} {2: .2f}|".format("" * 5, dd["d"][1, 0], dd["d"][1, 1])
