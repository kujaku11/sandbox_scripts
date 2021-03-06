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
page_id = "5b4008bfe4b060350a10c69e"
username = "jpeacock@usgs.gov"
password = getpass.getpass()

page_citation = (
    "Peacock, J. R, Denton, K. M., and Ponce, D. A., 2019, "
    + "Magnetotelluric data from Mountain Pass, California, 2015: "
    + "U.S. Geological Survey Data Release, "
    + "https://doi.org/10.5066/P9JNPLPJ."
)

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
        print("---> skipping child id {0}".format(child_id))
        continue

    # need to add back in edi and png files
    station = child_json["title"].split()[1].strip()

    ### page citation
    child_json["citation"] = page_citation

    #### UPDATE CHILD ITEM
    sb_session.update_item(child_json)


# =======

#    child_json['citation'] = page_citation
##    ### sort order of files
##    fn_dict = {'zip':[]}
##    for f_dict in child_json['files']:
##        fname = f_dict['name']
##        if fname.endswith('.edi'):
##            fn_dict['edi'] = f_dict
##        elif fname.endswith('.png'):
##            fn_dict['png'] = f_dict
##        elif fname.endswith('xml'):
##            fn_dict['xml'] = f_dict
##        elif fname.endswith('zip'):
##            fn_dict['zip'].append(f_dict)
##        else:
##            continue
##
##    # sort zip files by date
##    zip_fn_list = sorted(fn_dict['zip'], key=lambda k: k['name'])
##
##    # make new list of file dictionaries
##    fn_list = [fn_dict['xml'], fn_dict['edi'], fn_dict['png']]
##    child_json['files'] = fn_list + zip_fn_list
#
#    ### change web links
#    child_json['webLinks'] = [child_json['webLinks'][0]]
# >>>>>>> f5d3b1ab01a81c55641a4e3c09d6ee60ecebd6f1
#    ### remove the double doi in the citation
#    https_find_01 = child_json['citation'].find('https')
#    https_find_02 = child_json['citation'].find('https', https_find_01+5)
#
#    child_json['citation'] = child_json['citation'][0:https_find_01]+\
#                             child_json['citation'][https_find_02:]
#
#    ### sort order of files
#    edi_find = False
#    xml_find = False
#    png_find = False
#    fn_dict = {'zip':[]}
#    for f_dict in child_json['files']:
#        fname = f_dict['name']
#        if fname.endswith('.edi'):
#            fn_dict['edi'] = f_dict
#            edi_find = True
#        elif fname.endswith('.png'):
#            fn_dict['png'] = f_dict
#            png_find = True
#        elif fname.endswith('xml'):
#            fn_dict['xml'] = f_dict
#            xml_find = True
#        elif fname.endswith('zip'):
#            fn_dict['zip'].append(f_dict)
#        else:
#            continue
#
#    # sort zip files by date
#    zip_fn_list = sorted(fn_dict['zip'], key=lambda k: k['name'])

# make new list of file dictionaries
#    if not edi_find:
#        if os.path.isfile(edi_fn):
#            child_json = sb_session.upload_file_to_item(child_json, edi_fn, scrape_file=False)
#            fn_list = [fn_dict['xml'], os.path.basename(edi_fn)]
#        if not png_find:
#            if os.path.isfile(png_fn):
#                child_json = sb_session.upload_file_to_item(child_json, png_fn, scrape_file=False)
#                fn_list = [fn_dict['xml'], os.path.basename(edi_fn), os.path.basename(png_fn)]
#        else:
#            fn_list = [fn_dict['xml'], fn_dict['png']]
#    else:
#        fn_list = [fn_dict['xml'], fn_dict['edi'], fn_dict['png']]
#    child_json['files'] = fn_list + zip_fn_list
#
#    child_json['summary'] = child_json['summary'].replace('146', '147')
