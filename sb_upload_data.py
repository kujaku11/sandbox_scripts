#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 10:56:34 2018

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import os
import datetime
import sys
import getpass

import mtpy.usgs.usgs_archive as archive
# =============================================================================
# Inputs
# =============================================================================
archive_dir = r"/media/jpeacock/My Passport/iMUSH/Archive"

# =============================================================================
# Upload Parameters
# =============================================================================
page_id = '5ad77f06e4b0e2c2dd25e798'
username = 'jpeacock@usgs.gov'
# =============================================================================
# Upload data
# =============================================================================
if __name__ == "__main__":
    
    password = getpass.getpass()
    st = datetime.datetime.now()
    station = sys.argv[1]
    if station.find('[') == 0:
        station_list = station.replace('[', '').replace(']', '').split(',')
        station_list = [ss.strip() for ss in station_list]
    else:
        station_list = [station]
    
    print(station_list, type(station_list))
    for sb_station in station_list:
        station_item = archive.sb_upload_data(page_id,
                                              os.path.join(archive_dir, sb_station),
                                              username,
                                              password)  
    et = datetime.datetime.now()
    t_diff = et-st
    print('---> Archived {0}'.format(station))
    print('     Took {0:.0f}:{1:02.2f}'.format(int(t_diff.total_seconds()//60),
                                              t_diff.total_seconds()%60))
    print('     Ended at {0}'.format(datetime.datetime.ctime(datetime.datetime.now()))) 
    

