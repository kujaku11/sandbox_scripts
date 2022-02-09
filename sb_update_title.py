# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 09:07:30 2021

@author: jpeacock
"""
import os
import sciencebasepy as sb
import time

page_id = "60dcb385d34e3a6dca21e4b9"
username = "jpeacock@usgs.gov"


# initialize a session
session = sb.SbSession()

# login to session, note if you run this in a console your password will
# be visible, otherwise run from a command line > python sciencebase_upload.py
session.loginc(username)

# need to wait a few seconds to connect otherwise bad things happen
time.sleep(5)

count = 0
for child in session.get_child_ids(page_id):
    page_dict = session.get_item(child)
    # if "station" in page_dict["title"].lower():
    #     station = page_dict["title"].split()[-1].strip()
    #     page_dict["title"] = f"Magnetotelluric and TEM Data from the Umatilla Indian Reservation Geothermal Resources Assessment: Phase 2, 2020: station {station}"
    #     session.update_item(page_dict)
    #     print(f"--> {count}: Updated {station}")
    #     count += 1
        
    if "station" in page_dict["title"].lower():
        page_dict["citation"] = page_dict["citation"].replace(", https", "US Geological Survey data release, https")
        session.update_item(page_dict)
        # print(f"--> {count}: Updated {station}")
        # count += 1
