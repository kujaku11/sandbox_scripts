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
station_dir = r"d:\Peacock\MTData\SanPabloBay"
# full path to the newly created survey configureation file
survey_cfg_fn = r"d:\Peacock\MTData\SanPabloBay\StationInfo_SanPabloBay_2015.cfg"

# copy path to put .edi files in a common directory
edi_copy_path = r"d:\Peacock\MTData\SanPabloBay\EDI_Files"

station_list = ['sp{0:02}'.format(ii) for ii in range(1, 16)]
station_list.remove('sp11')

#for folder in os.listdir(station_dir):
# loop over station folder, here we are just looking at one, if there was 
# more you can add them to the list
for folder in station_list[8:]:
        # the folder that the .avg files are in, that name, for me in this
        # case its 4. 
        ss = '{0:01}'.format(int(folder[2:]))
       
        # the directory where the .avg folder is
        avg_dir = os.path.join(station_dir, folder, 'Merged')
        
        # mtft configuration file
        mtft_cfg_fn = os.path.join(station_dir, folder, 'Merged', 'mtft24.cfg')
        
        # mtedit configuration file
        mtedit_cfg_fn = os.path.join(avg_dir, ss, 'mtedit.cfg')
        
        # make a ZongeMTAvg object
        zavg_obj = zonge.ZongeMTAvg()
        zavg_obj.avg_dict = {'ex':ss, 'ey':ss}
        
        # loop through all the types of .avg file just to have them
        for ext in ['ga.avg', 'dp.avg', 'ps.avg']:
            zavg_obj.write_edi(avg_dir, folder,
                               survey_cfg_file=survey_cfg_fn,
                               mtft_cfg_file=mtft_cfg_fn,
                               mtedit_cfg_file=mtedit_cfg_fn,
                               copy_path=r"{0}_{1}".format(edi_copy_path, 
                                                           ext[0:2]),
                               avg_ext=ext)
        
