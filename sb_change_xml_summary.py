# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 14:19:44 2018

@author: jpeacock
"""

import os

archive_dir = r"h:\iMUSH\Archive"

for station in os.listdir(archive_dir):
    if station[0:3] == "msh":
        station_dir = os.path.join(archive_dir, station)
        xml_fn = os.path.join(station_dir, "{0}_meta.xml".format(station))
        if os.path.isfile(xml_fn):
            with open(xml_fn, "r") as fid:
                xml_str = fid.read()

            ### replace 146 with 147
            xml_str = xml_str.replace("146", "147")
            xml_str = xml_str.replace("<issue>,</issue>", "<issue>11</issue>")
            with open(xml_fn, "w") as fid:
                fid.write(xml_str)
        if os.path.isfile(xml_fn[:-4] + "_01.xml"):
            os.remove(xml_fn[:-4] + "_01.xml")
