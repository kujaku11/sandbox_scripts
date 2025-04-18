# -*- coding: utf-8 -*-
"""
Created on Tue Jul 05 18:24:24 2016

@author: peacock

Notes update 9/25/21 (Dolan Lucero)
Changed variables for most recent update of MTpy...
"""


# ==============================================================================
# Imports
# ==============================================================================
import mtpy.usgs.zen as zen
import mtpy.usgs.zen_processing as zen_processing
import os

# ==============================================================================
# Variables
# ==============================================================================
# directory where all your station data is stored.  You will probably have to
# change this a little bit if you use the Zonge software to download the data
# I'm not sure what there structure is, I don't really use it.  You might need
# to add some more for loops or something to track down where the Z3D files
# are.  The way I have it is each station is a folder and then in that folder
# is all the Z3D files.
station_dir = r"C:\Users\Dolan\Downloads\RMT013"

# file name stem, it will save as StationInfo_f_stem.cfg"
f_stem = "RinconTest"

# make an empty dictionary to put stuff in to
config_dict = {}

# now loop over each station in the directory path and find the Z3D files to
# get the header information and put it into a configuration file
for folder in os.listdir(station_dir):
    # check to see if the folder is actually a directory
    if os.path.isdir(os.path.join(station_dir, folder)) is True:

        # get the first Z3D file in that station folder
        z3d_fn = [
            os.path.join(station_dir, folder, fn)
            for fn in os.listdir(os.path.join(station_dir, folder))
            if fn[-4:] == ".z3d"
        ][0]
        # read in the Z3D header, metadata and schedule
        z3d_obj = zen.Zen3D(z3d_fn)
        z3d_obj._read_header()
        z3d_obj._read_metadata()
        z3d_obj._read_schedule()

        # make a survey config object and put the Z3D information into it
        # you can make this more accurate if you want by filling other
        # attributes of st_obj
        st_obj = zen_processing.SurveyConfig()
        st_obj.box = z3d_obj.header.box_number
        st_obj.date = z3d_obj.schedule.Date
        st_obj.elevation = z3d_obj.header.alt
        st_obj.lat = z3d_obj.header.lat
        st_obj.lon = z3d_obj.header.long
        st_obj.station = folder
        st_obj.location = "Rincon"
        st_obj.network = "Rincon"

        # Add that information into the empty dictionary to write later
        config_dict[folder] = st_obj.__dict__

# write the station configuration file to that station directory
zen_processing.mtcfg.write_dict_to_configfile(
    config_dict, os.path.join(station_dir, "StationInfo{0}.cfg".format(f_stem))
)
