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
page_url = '5ad77f06e4b0e2c2dd25e798'
username = 'jpeacock@usgs.gov'
password = getpass.getpass()

# =============================================================================
# login and get child ids
# =============================================================================
sb_session = sb.SbSession()
sb_session.login(username, password)

child_ids = sb_session.get_child_ids(page_url)
# =============================================================================
# Change citation
# =============================================================================
for child_id in child_ids:
    child_json = sb_session.get_item(child_id)
    
    https_find_01 = child_json['citation'].find('https')
    https_find_02 = child_json['citation'].find('https', https_find_01+5)
    
    child_json['citation'] = child_json['citation'][0:https_find_01]+\
                             child_json['citation'][https_find_02:]
    
    sb_session.update_item(child_json)
