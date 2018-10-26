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
import sciencebasepy as sb
import time
import getpass

# =============================================================================
# Inputs
# =============================================================================
archive_dir = r"/media/jpeacock/My Passport/iMUSH/Archive"

# =============================================================================
# Upload Parameters
# =============================================================================
page_id = '5ad77f06e4b0e2c2dd25e798'
username = 'jpeacock@usgs.gov'
#password = getpass.getpass()

station = 'mshE012'
# =============================================================================
# Science Base Functions
# =============================================================================
def locate_child_item(sb_session, station, sb_url):
    """
    see if there is a child item already for the given station.
    """
    for item_id in sb_session.get_child_ids(sb_url):
        item_title = sb_session.get_item(item_id, {'fields':'title'})['title']
        if station in item_title:
            return item_id
    
    return False

def sort_fn_list(fn_list):
    """
    sort the file name list to xml, edi, png
    """
    
    fn_list_sort = [None, None, None]
    index_dict = {'xml':0, 'edi':1, 'png':2}
    
    for ext in ['xml', 'edi', 'png']:
        for fn in fn_list:
            if fn.endswith(ext):
                fn_list_sort[index_dict[ext]] = fn
                fn_list.remove(fn)
                break
    fn_list_sort += sorted(fn_list)
    
    # check to make sure all the files are there
    if fn_list_sort[0] is None:
        print('\t\t!! No .xml file found !!')
    if fn_list_sort[1] is None:
        print('\t\t!! No .edi file found !!')
    if fn_list_sort[2] is None:
        print('\t\t!! No .png file found !!')
        
    # get rid of any Nones in the list in case there aren't all the files
    fn_list_sort[:] = (value for value in fn_list_sort if value is not None)
        
    return fn_list_sort

def sb_session_login(sb_session, sb_username, sb_password=None):
    """
    login in to sb session
    """
    
    if not sb_session.is_logged_in():
        if sb_password is None:
            sb_session.loginc(sb_username)
        else:
            sb_session.login(sb_username, sb_password)
        time.sleep(5)
    
    return sb_session

def get_fn_list(archive_dir):
    """
    get the list of files to archive looking for .zip, .edi, .png
    
    sort according .xml, .edi, .png, .zip
    
    return the list of files
    """
    
    fn_list = [os.path.join(archive_dir, fn) 
               for fn in os.listdir(archive_dir)
               if fn.endswith('.zip') or fn.endswith('.xml') or 
               fn.endswith('.edi') or fn.endswith('.png')]
    
    return sort_fn_list(fn_list)
    
    
def upload_data_to_sb(sb_page_id, archive_station_dir, sb_username, 
                      sb_password=None):
    ### initialize a session
    session = sb.SbSession()
    
    ### login to session, note if you run this in a console your password will
    ### be visible, otherwise run from a command line > python sciencebase_upload.py
    sb_session_login(session, sb_username, sb_password)
    
    station = os.path.basename(archive_station_dir)

    ### File to upload
    upload_fn_list = get_fn_list(archive_station_dir)
    
    ### check if child item is already created
    child_id = locate_child_item(session, station, sb_page_id)
    ## it is faster to remove the child item and replace it all
    if child_id:
        session.delete_item(session.get_item(child_id))
        sb_action = 'Updated'
            
    else:
        sb_action = 'Created'
    
    ### make a new child item 
    new_child_dict = {'title':'station {0}'.format(station),
                      'parentId':page_id,
                      'summary': 'Magnetotelluric data'}
    new_child = session.create_item(new_child_dict)
    
    # sort list so that xml, edi, png, zip files
    # upload data
    try:
        item = session.upload_files_and_upsert_item(new_child, upload_fn_list)
    except:
        sb_session_login(session, sb_username, sb_password)
        # if you want to keep the order as read on the sb page, 
        # need to reverse the order cause it sorts by upload date.
        for fn in upload_fn_list[::-1]:
            try:
                item = session.upload_file_to_item(new_child, fn)
            except:
                print('\t +++ Could not upload {0} +++'.format(fn))
                continue
        
    print('==> {0} child for {1}'.format(sb_action, station))
    
    session.logout()
    
    return item

# =============================================================================
# Upload data
# =============================================================================
#station_item = upload_data_to_sb(page_id, os.path.join(archive_dir, station),
#                                 username, password)