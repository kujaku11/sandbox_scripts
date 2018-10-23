#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 12:52:29 2018

@author: jpeacock
"""
import os
import sciencebasepy as sb
import time

# =============================================================================
# Parameters
# =============================================================================
page_id = '5ad77f06e4b0e2c2dd25e798'
username = 'jpeacock@usgs.gov'

archive_dir = r"/mnt/hgfs/MTData/iMUSH_Zen_samples/imush/Archive"
# =============================================================================
# 
# =============================================================================
### initialize a session
session = sb.SbSession()

### login to session, note if you run this in a console your password will
### be visible, otherwise run from a command line > python sciencebase_upload.py
session.loginc(username)

# need to wait a few seconds to connect otherwise bad things happen
time.sleep(5)

### update file
#item_to_change = session.get_item(item_id)
#session.upload_files_and_upsert_item(item_to_change, [file_list])


#### loop over stations and make a child item for each 
#for station in os.listdir(archive_dir):
#    station_path = os.path.join(archive_dir, station)
#    if os.path.isdir(station_path):
#        new_child_dict = {'title':'station {0}'.format(station),
#                         'parentId':page_id,
#                         'summary': 'Magnetotelluric data'}
#        new_child = session.create_item(new_child_dict)
#        
#        # upload files
#        fn_list = [os.path.join(station_path, fn) for fn in os.listdir(station_path)
#                   if fn.endswith('.zip') or fn.endswith('.xml')]
#        
#        item = session.upload_files_and_update_item(new_child, fn_list)
#        
#        
#        print('==> Created child for {0}'.format(station))


### Delete all child items
# session.delete_items(session.get_child_ids(page_url))
        
### update json
#page_dict = session.get_json('https://sciencebase.gov/catalog/item/{0}'.format(page_id))
#page_dict['citation'] = u'Paul A. Bedrosian, Jared R. Peacock, Esteban Bowles-Martinez, and Adam Schultz, 2018, Magnetotelluric data from the imaging Magma Under St. Helens (iMUSH) project: U.S. Geological Survey, https://doi.org/10.5066/P9NLXXB3.'
#session.update_item(page_dict)

###
