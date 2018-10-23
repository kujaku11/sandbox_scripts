# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 12:55:59 2018

@author: jpeacock
"""
import os
import sys
from cStringIO import StringIO
import mtpy.usgs.usgs_archive as archive
import datetime
import zipfile
import sciencebasepy as sb
import time
import getpass

# =============================================================================
# Inputs
# =============================================================================
survey_dir = r"/media/jpeacock/My Passport/iMUSH"
survey_csv = r"/media/jpeacock/My Passport/iMUSH/imush_archive_summary_edited_final.csv"
survey_cfg = r"/media/jpeacock/My Passport/iMUSH/imush_archive_PAB.cfg"

# =============================================================================
# Upload Parameters
# =============================================================================
page_id = '5ad77f06e4b0e2c2dd25e798'
username = 'jpeacock@usgs.gov'
password = getpass.getpass()

# survey name and abbreviation
survey = 'iMUSH'
stem = 'msh'

# declination, set to 0 if declination is already included in the measurements
declination = 15.5

# srite survey xml, csv
write_survey_info = True

# write ascii files
write_asc = True

# write the full ascii file or not
write_full = True

# upload data to science base
upload_data = True
# =============================================================================
# Get station list from csv file
# =============================================================================
scfg = archive.USGScfg()
survey_db = scfg.read_survey_csv(survey_csv)
station_list = [s[3:] for s in survey_db.siteID]
#station_list = ['F012']
# =============================================================================
# Make an archive folder to put everything
# =============================================================================
save_dir = os.path.join(survey_dir, 'Archive')
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
    
# =============================================================================
# class for capturing the output to store in a file
# =============================================================================
# this should capture all the print statements
class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout
        
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
    return fn_list_sort
    
def upload_data_to_sb(sb_page_id, archive_station_dir, sb_username, 
                      sb_password=None):
    ### initialize a session
    session = sb.SbSession()
    
    ### login to session, note if you run this in a console your password will
    ### be visible, otherwise run from a command line > python sciencebase_upload.py
    if sb_password is None:
        session.loginc(username)
    else:
        session.login(username, sb_password)
    # need to wait a few seconds to connect otherwise bad things happen
    time.sleep(5)
    
    station = os.path.basename(archive_station_dir)

    ### File to upload
    fn_list = [os.path.join(archive_station_dir, fn) 
               for fn in os.listdir(archive_station_dir)
               if fn.endswith('.zip') or fn.endswith('.xml') or 
               fn.endswith('.edi') or fn.endswith('.png')]
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
    fn_list = fn_list[-3:]+fn_list[0:-3]
    item = session.upload_files_and_upsert_item(new_child, sort_fn_list(fn_list))
    
    print('==> {0} child for {1}'.format(sb_action, station))
    
    session.logout()
    
    return item
# =============================================================================
# make the files
# =============================================================================
survey_xml = archive.XMLMetadata()
survey_xml.read_config_file(survey_cfg)

st = datetime.datetime.now()
#for station in os.listdir(survey_dir)[132:]:
for station in station_list[:]:
    try:
        station_path = os.path.join(survey_dir, station)
        station_save_dir = os.path.join(save_dir, stem+station)
    
        if os.path.isdir(station_path):
            zc = archive.Z3DCollection()
            # check to see if there are .z3d files in the folder, if not continue
            try:
                fn_list = zc.get_time_blocks(station_path)
            except IndexError:
                print('*** Skipping folder {0} ***'.format(station))
                continue
            
            # make station folder
            if not os.path.exists(station_save_dir):
                os.mkdir(station_save_dir)
            
            zm = archive.USGSasc()
            zm.CoordinateSystem = 'Geographic North'
            zm.declination = declination
            asc_fn_list = ['{0}{1}'.format(stem+station, ext) for ext in 
                           ['.edi', '.png']]
            
            s_st = datetime.datetime.now()
            # capture the output to put into a log file for each station, just to
            # be sure and capture what happened.
            with Capturing() as output:
                for fn_block in fn_list:
                    zm.get_z3d_db(fn_block)
    
                    # put in survey name and rename the station with the stem
                    zm.SurveyID = survey
                    zm.SiteID = stem+zm.SiteID
                    
                    # look information in configuration files
                    # Note need to do this after renaming the station
                    if survey_csv is not None:
                        mtft_find = zm.get_metadata_from_survey_csv(survey_csv)
                    else:
                        mtft_find = zm.get_metadata_from_mtft24_cfg()
                
                    # flip Zen18 channel Hx
                    if 'ZEN18' in [zm.channel_dict[chn]['InstrumentID'] for chn 
                                   in zm.channel_dict.keys()]:
                        try:
                            zm.ts.hx *= -1
                            print('   --> ZEN 18: flipped HX')
                        except AttributeError:
                            print('   --> ZEN 18: no channel HX to flip')
        
                    # write out the ascii file if desired
                    if write_asc:
                        zm.write_asc_file(save_dir=station_save_dir,
                                          full=write_full, 
                                          compress=False,
                                          compress_type='zip')
                        # get file name
                        asc_fn = zm._make_file_name(save_path=station_save_dir, 
                                                    compression=False)
                        # need to zip the files outside of making them for some
                        # reason can't do it in the function.
                        with zipfile.ZipFile(asc_fn+'.zip', 'w') as zip_fid:
                            zip_fid.write(asc_fn, 
                                          os.path.basename(asc_fn),
                                          zipfile.ZIP_DEFLATED)
                            os.remove(asc_fn)
                        # append file name to the list that goes in the xml    
                        asc_fn_list.append(os.path.basename(asc_fn))
                    
                    # write out metadata
                    zm.write_station_info_metadata(save_dir=station_save_dir,
                                                   mtft_bool=mtft_find)
                    
                # make a station database
                s_cfg = archive.USGScfg()
                s_db, csv_fn = s_cfg.combine_run_cfg(station_save_dir)
                
                # make xml file
                s_xml = archive.XMLMetadata()
                s_xml.read_config_file(survey_cfg)
                s_xml.supplement_info = s_xml.supplement_info.replace('\\n', '\n\t\t\t')
                
                # add station name to title
                s_xml.title += ', station {0}'.format(stem+station)
                
                # location
                s_xml.survey.east = s_db.lon.median()
                s_xml.survey.west = s_db.lon.median()
                s_xml.survey.north = s_db.lat.median()
                s_xml.survey.south = s_db.lat.median()
                
                # get elevation from national map
                s_elev = archive.get_nm_elev(s_db.lat.median(), 
                                             s_db.lon.median()) 
                s_xml.survey.elev_min = s_elev
                s_xml.survey.elev_max = s_elev
                
                # start and end time
                s_xml.survey.begin_date = s_db.start_date.min()
                s_xml.survey.end_date = s_db.stop_date.max()
                
                # add list of files
                s_xml.supplement_info += '\n\t\t\tFile List:\n\t\t\t'+'\n\t\t\t'.join(asc_fn_list)
                
                # write station xml
                s_xml.write_xml_file(os.path.join(station_save_dir, 
                                                  '{0}_meta.xml'.format(stem+station)), 
                                    write_station=True)
                
            if upload_data:
                sb_item = upload_data_to_sb(page_id, 
                                            station_save_dir, 
                                            username,
                                            password)
            
            #--> write log file
            log_fid = open(os.path.join(station_save_dir, 
                                        '{0}_Archive.log'.format(stem+station)), 'w')
            log_fid.write('\n'.join(output))
            log_fid.close()
            
            s_et = datetime.datetime.now()
            station_diff = s_et - s_st
            
            print('--> Archived station {0}, took {1}:{2:02.2f}, finished at {3}'.format(station, 
                                              int(station_diff.total_seconds()//60),
                                              station_diff.total_seconds()%60,
                                              datetime.datetime.ctime(datetime.datetime.now())))
    except:
        print('xxx --> skipping {0} <---xxx'.format(station))

# adjust survey information to align with data
if write_survey_info:        
    survey_cfg_obj = archive.USGScfg()
    survey_db, csv_fn, location_fn = survey_cfg_obj.combine_all_station_info(save_dir)
    survey_xml.supplement_info = survey_xml.supplement_info.replace('\\n', '\n\t\t\t')
    survey_cfg_obj.write_shp_file(csv_fn, save_path=save_dir)
    
    # location
    survey_xml.survey.east = survey_db.lon.min()
    survey_xml.survey.west = survey_db.lon.max()
    survey_xml.survey.south = survey_db.lat.min()
    survey_xml.survey.north = survey_db.lat.max()
    
    # get elevation min and max from station locations, not sure if this is correct
    survey_xml.survey.elev_min = survey_db.nm_elev.min()
    survey_xml.survey.elev_max = survey_db.nm_elev.max()
    
    # dates
    survey_xml.survey.begin_date = survey_db.start_date.min()
    survey_xml.survey.end_date = survey_db.stop_date.max()
    
    ### --> write survey xml file
    survey_xml.write_xml_file(os.path.join(save_dir, 
                                           '{0}.xml'.format(stem+survey)))

# print timing
et = datetime.datetime.now()
t_diff = et-st
print('--> Archiving took: {0}:{1:02.2f}, finished at {2}'.format(int(t_diff.total_seconds()//60),
                                              t_diff.total_seconds()%60,
                                              datetime.datetime.ctime(datetime.datetime.now())))
        
