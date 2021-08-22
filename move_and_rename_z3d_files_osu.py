# -*- coding: utf-8 -*-
"""
Created on Tue May 29 13:49:13 2018

Move Z3D files into a single folder and rename the files

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import os
import shutil
import mtpy.usgs.zen as zen

# =============================================================================
# parameters
# =============================================================================
dir_path = r"g:\iMUSH\OSU_2015\normal"

# =============================================================================
#
# =============================================================================
# loop over stations
for station_folder in os.listdir(dir_path):
    station_path = os.path.join(dir_path, station_folder)
    if os.path.isdir(station_path):
        station = os.path.basename(station_path)[0:4]
        for date_folder in os.listdir(station_path):
            date_path = os.path.join(station_path, date_folder)
            # look in the date folder
            if os.path.isdir(date_path):
                for zen_folder in os.listdir(date_path):
                    zen_path = os.path.join(date_path, zen_folder)
                    # look in the instrument folder, there should be only one
                    if os.path.isdir(zen_path):
                        for chn_folder in os.listdir(zen_path):
                            chn_path = os.path.join(zen_path, chn_folder)
                            if (
                                os.path.isfile(chn_path)
                                and chn_folder.lower() == "mtft24.cfg"
                            ):
                                try:
                                    os.rename(
                                        chn_path,
                                        os.path.join(
                                            station_path,
                                            "{0}_mtft24.cfg".format(station),
                                        ),
                                    )
                                except WindowsError:
                                    try:
                                        os.rename(
                                            chn_path,
                                            os.path.join(
                                                station_path,
                                                "{0}_mtft24_01.cfg".format(station),
                                            ),
                                        )
                                    except WindowsError:
                                        os.rename(
                                            chn_path,
                                            os.path.join(
                                                station_path,
                                                "{0}_mtft24_02.cfg".format(station),
                                            ),
                                        )
                            # look into each channel folder
                            elif os.path.isdir(chn_path):
                                for z3d_fn in os.listdir(chn_path):
                                    if z3d_fn.lower().endswith(".z3d"):
                                        fn_path = os.path.join(chn_path, z3d_fn)
                                        # skip the small files
                                        if os.stat(fn_path).st_size < 350000L:
                                            continue
                                        # read in just the metadata
                                        z_obj = zen.Zen3D(fn_path)
                                        z_obj.read_all_info()
                                        z_obj.station = station

                                        channel = z_obj.metadata.ch_cmp.upper()
                                        st = z_obj.schedule.Time.replace(":", "")
                                        sd = z_obj.schedule.Date.replace("-", "")
                                        # make a new useful file name
                                        sv_fn = "{0}_{1}_{2}_{3}_{4}.Z3D".format(
                                            station, sd, st, int(z_obj.df), channel
                                        )
                                        # rename that file instead of copy, way faster
                                        os.rename(
                                            fn_path, os.path.join(station_path, sv_fn)
                                        )
                # remove the OSU directory tree
                # shutil.rmtree(date_path)
