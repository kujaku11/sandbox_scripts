# -*- coding: utf-8 -*-
"""
Please see README.md (https://github.com/esturdivant-usgs/science-base-automation) for detailed instructions.

sb_automation.py

By: Emily Sturdivant, esturdivant@usgs.gov

Modified by Phil Brown, pbrown@usgs.gov 04/19/2018 to upload ALL files in a directory and only have one child per record

OVERVIEW: Script creates child pages that mimic the directory structure and
populates the pages using a combination of fields from the landing page and the metadata.
Directories within home must be named as desired for each child page.
Currently, the script creates a new child page for each metadata file.

REQUIRES: pysb, lxml, config_autoSB.py, autoSB.py
To install pysb with pip: pip install -e git+https://my.usgs.gov/stash/scm/sbe/pysb.git#egg=pysb
"""

#%% Import packages
import pysb # Install on OSX with "pip install -e git+https://my.usgs.gov/stash/scm/sbe/pysb.git#egg=pysb"
import os
import glob
from lxml import etree
import json
import pickle
import datetime
import sys
import shutil
from pathlib import Path
try:
	sb_auto_dir = os.path.dirname(os.path.realpath(__file__))
except:
	sb_auto_dir = os.path.dirname(os.path.realpath('sb_automation.py'))
sys.path.append(sb_auto_dir) # Add the script location to the system path just to make sure this works.
from autoSB import *
from config_autoSB import *


#%% Initialize SB session
"""
sb = log_in(useremail)
"""
# get JSON item for parent page
landing_item = sb.get_item(landing_id)
#print("CITATION: {}".format(landing_item['citation'])) # print to QC citation
# make dictionary of ID and URL values to update in XML
new_values = {'landing_id':landing_item['id'], 'doi':dr_doi}
if 'pubdate' in locals():
	new_values['pubdate'] = pubdate
if 'find_and_replace' in locals():
	new_values['find_and_replace'] = find_and_replace
if 'metadata_additions' in locals():
	new_values['metadata_additions'] = metadata_additions
if "metadata_replacements" in locals():
	new_values['metadata_replacements'] = metadata_replacements
if "remove_fills" in locals():
	new_values['remove_fills'] = remove_fills

#%% Work with landing page and XML
"""
Work with landing page and XML
"""
# Remove all child pages
if replace_subpages:
    print(delete_all_children(sb, landing_id))
    landing_item = remove_all_files(sb, landing_id)

# Set imagefile
if 'previewImage' in subparent_inherits:
	for f in os.listdir(parentdir):
		if f.lower().endswith(('png','jpg','gif')):
			imagefile = os.path.join(parentdir,f)
elif "previewImage" in locals():
	if os.path.isfile(previewImage):
		imagefile = previewImage
	else:
		print("{} does not exist.".format(previewImage))
else:
	imagefile = False

#%% Create SB page structure
"""
Create SB page structure: nested child pages following directory hierarchy
Inputs: parent directory, landing page ID
This one should overwrite the entire data release (excluding the landing page).
"""
# Check whether logged in.
if not sb.is_logged_in():
	print('Logging back in...')
	try:
		sb = pysb.SbSession(env=None).login(useremail,password)
	except NameError:
		sb = pysb.SbSession(env=None).loginc(useremail)

# If there's no id_to_json.json file available, we need to create the subpage structure.
if not update_subpages and not os.path.isfile(os.path.join(parentdir,'id_to_json.json')):
	print("id_to_json.json file is not in parent directory, so we will perform update_subpages routine.")
	update_subpages = True 
	#update_subpages = False #PJB
	
# List XML files
xmllist = glob.glob(os.path.join(parentdir, '**/*.xml'), recursive=True)

if update_subpages:
    dict_DIRtoID, dict_IDtoJSON, dict_PARtoCHILDS = setup_subparents(sb, parentdir, landing_id, xmllist, imagefile)#PJB must get xml name and insert here in place of parentdir - fixed in function
else: # Import pre-created dictionaries if all SB pages exist
    with open(os.path.join(parentdir,'dir_to_id.json'), 'r') as f:
        dict_DIRtoID = json.load(f)
    with open(os.path.join(parentdir,'id_to_json.json'), 'r') as f:
        dict_IDtoJSON = json.load(f)
    with open(os.path.join(parentdir,'parentID_to_childrenIDs.txt'), 'rb') as f:
        dict_PARtoCHILDS = pickle.load(f)


#%% Create and populate data pages
"""
Create and populate data pages
Inputs: parent directory, landing page ID, dictionary of new values (new_values)
For each XML file in each directory, create a data page, revise the XML, and upload the data to the new page
"""
if verbose:
	print('---\nChecking log in information...')
#sb = log_in(useremail) #FIXME
if not sb.is_logged_in():
	print('Logging back in...')
	try:
		sb = pysb.SbSession(env=None).login(useremail,password)
	except NameError:
		sb = pysb.SbSession(env=None).loginc(useremail)

if verbose:
	print('Checking for directory: ID dictionary...')
if not "dict_DIRtoID" in locals():
	with open(os.path.join(parentdir,'dir_to_id.json'), 'r') as f:
		dict_DIRtoID = json.load(f)


#%%
# For each XML file in each directory, create a data page, revise the XML, and upload the data to the new page
if verbose:
	print('\n---\nWalking through XML files to create/find a data page, update the XML file, and upload the data...')
cnt = 0

for xml_file in xmllist:
	if restore_original_xml and os.path.exists(xml_file+'_orig'):
		shutil.copy(xml_file+'_orig', xml_file)
	cnt += 1
	print("File {}: {}".format(cnt, xml_file))
	if not sb.is_logged_in():
		print('Logging back in...')
		try:
			sb = pysb.SbSession(env=None).login(useremail, password)
		except NameError:
			sb = pysb.SbSession(env=None).loginc(useremail)

		
#%% Children made in 1. - PJB
	# 1. GET VALUES from XML
	dirname = os.path.basename(os.path.split(xml_file)[0])
	parentid = dict_DIRtoID[dirname] # leave old parent Id and do not use directory id PJB - will not nest children?
	new_values['doi'] = dr_doi if 'dr_doi' in locals() else get_DOI_from_item(flexibly_get_item(sb, parentid))
	# Get title of data by parsing XML
	data_title = get_title_from_data(xml_file)

	# Create (or find) data page based on title
	# We just want to use existing 'subpage' item here instaed of recreating another child named data_item >>-PJB->
	# data_item = find_or_create_child(sb, parentid, data_title, verbose=verbose)	
	data_item = sb.get_item(parentid)  # Get existing item from ScienceBase >>-PJB->

	
		# If pubdate in new_values, set it as the date for the SB page
	##try:
		##data_item["dates"][0]["dateString"]= new_values['pubdate'] #FIXME add this to a function in a more generalized way?
	##except:
		##pass
#%%
	# 2. MAKE UPDATES
	# Update XML
	if update_XML:
		# add SB UID to be updated in XML
		new_values['child_id'] = data_item['id'] 
		# Look for browse graphic
		searchstr = xml_file.split('.')[0].split('_meta')[0] + '*browse*'
		try:
			browse_file = glob.glob(searchstr)[0]
			new_values['browse_file'] = browse_file.split('/')[-1]
		except Exception as e:
			print("We weren't able to upload a browse image for page {}. Exception reported as '{}'".format(dirname, e))

		# Make the changes to the XML based on the new_values dictionary
		##update_xml(xml_file, new_values, verbose=verbose) # new_values['pubdate']
		##if "find_and_replace" in new_values:
			##find_and_replace_from_dict(xml_file, new_values['find_and_replace'])
		##if verbose:
			##print("UPDATED XML: {}".format(xml_file))
			
	# Upload data to ScienceBase
	if update_data:
		# Upload all files in dir that match basename of XML file. Record list of files that were not uploaded because they were above the threshold set by max_MBsize	
		data_item, bigfiles1 = upload_files_matching_xml(sb, data_item, xml_file, max_MBsize=max_MBsize, replace=True, verbose=verbose)
		if bigfiles1:
			if not 'bigfiles' in locals():
				bigfiles = []
			bigfiles += bigfiles1
	# Upload XML to ScienceBase
	elif update_XML:
		# If XML was updated, but data was not uploaded, replace only XML.
		try:
			sb.replace_file(xml_file, data_item) # Does not update SB page to match metadata
		except e:
			print('Retry with update_data = True. pysb.replace_file() is not working for this use. Returned: \n'+e)
	if 'previewImage' in data_inherits and "imagefile" in locals():
		data_item = sb.upload_file_to_item(data_item, imagefile)
	if verbose:
		now_str = datetime.datetime.now().strftime("%H:%M:%S on %Y-%m-%d")
		print('Completed {} out of {} xml files at {}.\n'.format(cnt, len(xmllist), now_str))
	# store values in dictionaries
	dict_DIRtoID[xml_file] = data_item['id']
	dict_IDtoJSON[data_item['id']] = data_item
	dict_PARtoCHILDS.setdefault(parentid, set()).add(data_item['id']) #Note this PJB

#%% Pass down fields from parents to children
print("\n---\nPassing down fields from parents to children...")
inherit_topdown(sb, landing_id, subparent_inherits, data_inherits, verbose=verbose)

#%% BOUNDING BOX
if update_extent:
	print("\nGetting extent of child data for parent pages...")
	set_parent_extent(sb, landing_id, verbose=verbose)

# Preview Image
if add_preview_image_to_all:
	# org_map['IDtoJSON'] = upload_all_previewImages(sb, parentdir, org_map['DIRtoID'], org_map['IDtoJSON'])
	dict_IDtoJSON = upload_all_previewImages(sb, parentdir, dict_DIRtoID, dict_IDtoJSON)

# Save dictionaries
# with open(os.path.join(parentdir,'org_map.json'), 'w') as f:
# 	json.dump(org_map, f)
with open(os.path.join(parentdir,'dir_to_id.json'), 'w') as f:
	json.dump(dict_DIRtoID, f)
with open(os.path.join(parentdir,'id_to_json.json'), 'w') as f:
	json.dump(dict_IDtoJSON, f)
with open(os.path.join(parentdir,'parentID_to_childrenIDs.txt'), 'ab+') as f:
	pickle.dump(dict_PARtoCHILDS, f)

#%% QA/QC
if quality_check_pages:
	qcfields_dict = {'contacts':4, 'webLinks':0, 'facets':1}
	print('Checking that each page has: \n{}'.format(qcfields_dict))
	pagelist = check_fields2_topdown(sb, landing_id, qcfields_dict, verbose=False)


now_str = datetime.datetime.now().strftime("%H:%M:%S on %m/%d/%Y")
print('\n{}\nAll done! View the result at {}'.format(now_str, landing_link))
if 'bigfiles' in locals():
	if len(bigfiles) > 0:
		print("These files were too large to upload so you'll need to use the large file uploader:")
		#print(*bigfiles, sep = "\n")
