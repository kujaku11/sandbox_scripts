# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 17:39:21 2018

@author: jpeacock
"""

import os
import shutil
import mtpy.usgs.zen as zen

main_dir = r"d:\iMUSH"

notes = ["# Notes for stations"]

for survey in os.listdir(main_dir):
    survey_dir = os.path.join(main_dir, survey)
    if os.path.isdir(survey_dir):
        for station in os.listdir(survey_dir):
            station_dir = os.path.join(survey_dir, station)
            if (
                os.path.isdir(station_dir)
                and len(station) >= 4
                and station not in ["do_not_archive"]
            ):
                if station.find("_") > 0 and len(station) >= 4:
                    notes.append(station)
                station = station[0:4].upper()

                # make a folder in the main directory to save to
                sv_path = os.path.join(main_dir, station)
                if not os.path.exists(sv_path):
                    os.mkdir(sv_path)
                print("--- {0}".format(sv_path))
                # look for all Z3D files within a station folder
                for root, folders, files in os.walk(station_dir):
                    for fn in files:
                        if fn.endswith(".Z3D"):
                            fn_path = os.path.join(root, fn)
                            # skip the small files
                            if os.stat(fn_path).st_size < 350000L:
                                continue
                            if fn.count("_") == 4:
                                sv_fn = "_".join([station] + fn.split("_")[1:])
                                shutil.move(fn_path, os.path.join(sv_path, sv_fn))
                            else:
                                # read in just the metadata
                                z_obj = zen.Zen3D(fn_path)
                                z_obj.read_all_info()
                                z_obj.station = station
                                try:
                                    channel = z_obj.metadata.ch_cmp.upper()
                                except AttributeError:
                                    notes.append("***CHECK {0}".format(fn_path))
                                    continue
                                st = z_obj.schedule.Time.replace(":", "")
                                sd = z_obj.schedule.Date.replace("-", "")
                                # make a new useful file name
                                sv_fn = "{0}_{1}_{2}_{3}_{4}.Z3D".format(
                                    station, sd, st, int(z_obj.df), channel
                                )
                                # rename that file instead of copy, way faster
                                shutil.move(fn_path, os.path.join(sv_path, sv_fn))
                        #                            os.rename(fn_path,
                        #                                      os.path.join(station_path, sv_fn))
                        elif "mtft24.cfg" in fn:
                            shutil.move(
                                os.path.join(root, fn),
                                os.path.join(sv_path, "{0}_mtft24.cfg".format(station)),
                            )
                        else:
                            continue

### write out notes
with open(os.path.join(main_dir, "station_notes.txt"), "w") as fid:
    fid.write("\n".join(notes))
