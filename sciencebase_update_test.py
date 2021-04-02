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
page_id = "5ca7db54e4b0c3b0064e2f8b"
username = "jpeacock@usgs.gov"

edi_dir = r"d:\Peacock\MTData\GraniteSprings\granite_springs_edi"
png_dir = r"d:\Peacock\MTData\GraniteSprings\granite_springs_plots"
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


### loop over stations and make a child item for each
for child in session.get_child_ids(page_id):
    item_json = session.get_item(child)
    station = item_json["title"].split()[1].strip()
    fn_list = [
        os.path.join(edi_dir, "{0}.edi".format(station)),
        os.path.join(png_dir, "{0}.png".format(station)),
    ]
    item = session.upload_files_and_upsert_item(item_json, fn_list, scrape_file=False)
    fn_sort = [None, None, None, None]
    for f_dict in item["files"]:
        if f_dict["name"].endswith(".xml"):
            fn_sort[0] = f_dict
        elif f_dict["name"].endswith(".edi"):
            fn_sort[1] = f_dict
        elif f_dict["name"].endswith(".png"):
            fn_sort[2] = f_dict
        elif f_dict["name"].endswith(".mth5"):
            fn_sort[3] = f_dict

    fn_sort = [ff for ff in fn_sort if ff is not None]
    item["files"] = fn_sort

    session.update_item(item)

    print("=" * 40)
    print("    {0}".format(station))
    print("Uploaded {0}".format(fn_list))
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
# page_dict = session.get_json('https://sciencebase.gov/catalog/item/{0}'.format(page_id))
# page_dict['citation'] = u'Paul A. Bedrosian, Jared R. Peacock, Esteban Bowles-Martinez, and Adam Schultz, 2018, Magnetotelluric data from the imaging Magma Under St. Helens (iMUSH) project: U.S. Geological Survey, https://doi.org/10.5066/P9NLXXB3.'
# session.update_item(page_dict)

###
