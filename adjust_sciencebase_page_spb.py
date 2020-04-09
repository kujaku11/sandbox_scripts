# -*- coding: utf-8 -*-
"""
Adjust Sciencebase layout.

.. note:: Run in a Python shell to avoid having your password echoed on screen

Created on Wed Oct 24 11:35:51 2018

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import sciencebasepy as sb
import getpass

# =============================================================================
# Parameters
# =============================================================================
page_id = '5e45fc5ae4b0ff554f662cbe'
username = 'jpeacock@usgs.gov'
password = getpass.getpass()
              
page_summary = 'This dataset consists of 14 magnetotelluric (MT) stations '+\
               'collected in 2015 near San Pablo Bay, California along a '+\
               'east-northeast profile. The U.S. Geological Survey '+\
               'acquired these data to understand the fault geometry of '+\
               'the Hayward Fault and the Rodgers Creek Fault.'

# =============================================================================
# login and get child ids
# =============================================================================
sb_session = sb.SbSession()
sb_session.login(username, password)

child_ids = sb_session.get_child_ids(page_id)
# =============================================================================
# Change json
# =============================================================================
for child_id in child_ids:
    try:
        child_json = sb_session.get_item(child_id)
    except:
        print('---> skipping child id {0}'.format(child_id))
        continue
    
    ### adjust summary
    child_json['summary'] = page_summary
    
    
    #### UPDATE CHILD ITEM
    sb_session.update_item(child_json)
    
