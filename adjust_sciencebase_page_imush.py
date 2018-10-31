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

ng_citation = 'Bedrosian, P. A., Peacock, J. R., Bowles-Martinez, E., '+\
              'Schultz, A., Hill, G. J. (2018) Crustal inheritance '+\
              'and a top-down control on arc magmatism at Mount St. Helens,'+\
              ' Nature Geoscience, 11, p. 865-870.' 

# =============================================================================
# login and get child ids
# =============================================================================
sb_session = sb.SbSession()
sb_session.login(username, password)

child_ids = sb_session.get_child_ids(page_url)
# =============================================================================
# Change json
# =============================================================================
for child_id in child_ids:
    try:
        child_json = sb_session.get_item(child_id)
    except:
        print('---> skipping child id {0}'.format(child_id))
        continue
    
#    ### remove the double doi in the citation
#    https_find_01 = child_json['citation'].find('https')
#    https_find_02 = child_json['citation'].find('https', https_find_01+5)
#    
#    child_json['citation'] = child_json['citation'][0:https_find_01]+\
#                             child_json['citation'][https_find_02:]
#    
#    ### sort order of files
#    fn_dict = {'zip':[]}
#    for f_dict in child_json['files']:
#        fname = f_dict['name']
#        if fname.endswith('.edi'):
#            fn_dict['edi'] = f_dict
#        elif fname.endswith('.png'):
#            fn_dict['png'] = f_dict
#        elif fname.endswith('xml'):
#            fn_dict['xml'] = f_dict
#        elif fname.endswith('zip'):
#            fn_dict['zip'].append(f_dict)
#        else:
#            continue 
#        
#    # sort zip files by date
#    zip_fn_list = sorted(fn_dict['zip'], key=lambda k: k['name'])
#    
#    # make new list of file dictionaries
#    fn_list = [fn_dict['xml'], fn_dict['edi'], fn_dict['png']]
#    child_json['files'] = fn_list + zip_fn_list
    
    ### change web links
    child_json['webLinks'][0]['type'] = 'Publication that references this resource'
    child_json['webLinks'][0]['title'] = ng_citation
    
    ### update the child item, sometimes you need to try twice
    try:
        updated_child = sb_session.update_item(child_json)
    except:
        updated_child = sb_session.update_item(child_json)
    
