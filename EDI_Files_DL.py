# -*- coding: utf-8 -*-
"""
When I process the data, I put the .cac files in a separate folder called
Merged and rename the files.  This can easily be done with

>>> import mtpy.usgs.zen as zen
>>> zen.rename_cac_files(directory_where_cac_files_are, station_stem)

And the files will be renamed station_stemRxy_date_time_samplingrate.cac in 
Merged.  

Then process from the Merged folder.

Created on Sat Jun 13 19:14:51 2015

@author: jpeacock-pr

Notes update (matt folsom)
structure your folders inside the station directory with a station names eg MT001, MT002 etc.
inside each, ensure there is only one folder, named 1, 2, 3 etc that coincides with the station number.
in this folder are your fft, avg, mtv and mtedit config files.
inside the upper MT001 folder is also the MTft.cfg and mtmerge.cfg files, plus the z3d files. Don't forget
to make a survey configuration file first. 

Notes update 9/25/21 (Dolan Lucero)
changed variables to match newest verison of MTpy. To start, enter the directories for 1) where your MT data is
station_dir, 2) where your survey .cfg file is,survey_cfg_fn 3) where you would like the EDI files,edi_copy_path 
4) station number, counter = ##, if first station is 10 type counter = 10,  
"""
#==============================================================================
# Imports
#==============================================================================
import mtpy.usgs.zonge as zonge
import os

#==============================================================================
# Variables
#==============================================================================
# directory where station folder are
station_dir = r"C:\Users\Dolan\Downloads\RMT013"
# full path to the newly created survey configureation file
survey_cfg_fn = r"c:\Users\jpeacock\Downloads\stationinfo_rincon.cfg"

# copy path to put .edi files in a common directory
edi_copy_path = r"C:\Users\Dolan\Downloads\RMT013"

#for folder in os.listdir(station_dir):
# loop over station folder, here we are just looking at one, if there was 
# more you can add them to the list

ss = str(13) # change this to 1 if starting from station 1

# #Enter folder names of stations here
# for folder in ['RMT013']:

        # the folder that the .avg files are in
        
# # this works for up to 99 stations.  It pulls a str of the station number from the folder name
# if counter <= 9:
#     ss = folder[-1]
# else:
#     ss = folder[-2]+folder[-1]
    
# counter = counter+1
   
# # the directory where the .avg folder is
# avg_dir = os.path.join(station_dir, folder)

# .avg filename
avg_file = ss+'.avg'

# full path to .avg
avg_path = r"c:\Users\jpeacock\Downloads\13ga.avg"

# mtft configuration file
mtft_cfg_fn = r"c:\Users\jpeacock\Downloads\mtedit.cfg"

# mtedit configuration file
mtedit_cfg_fn = r"c:\Users\jpeacock\Downloads\mtedit.cfg"

# make a ZongeMTAvg object
zavg_obj = zonge.ZongeMTAvg()
zavg_obj.avg_dict = {'ex':ss, 'ey':ss}

# loop through all the types of .avg file just to have them
for ext in [avg_path]:
    zavg_obj.write_edi(avg_path, "RMT013",
                       survey_cfg_file=survey_cfg_fn,
                       mtft_cfg_file=mtft_cfg_fn,
                       mtedit_cfg_file=mtedit_cfg_fn,
                       copy_path=r"c:\Users\jpeacock\Downloads",
                       avg_ext=ext)

