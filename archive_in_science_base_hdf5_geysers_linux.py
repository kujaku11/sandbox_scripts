# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 16:53:51 2018

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import os
import shutil
import datetime 
import mth5.mth5 as mth5
import usgs_archive.usgs_archive as archive
import usgs_archive.usgs_sb_xml as sb_xml
import getpass

# =============================================================================
# Inputs
# =============================================================================
### path to station data
station_dir = r"/mnt/hgfs/MTData/Geysers"

### path to survey parameter spread sheet
csv_fn = None
#csv_fn = r"/mnt/hgfs/MTData/GraniteSprings/Archive/gsv_survey_summary.csv"

### path to mth5 configuration file
cfg_fn = r"/mnt/hgfs/MTData/Geysers/gz_mth5.cfg"

### path to xml configuration file
xml_cfg_fn = r"/mnt/hgfs/MTData/Geysers/gz_archive.cfg"

### path to calibration files
calibration_dir = r"/mnt/hgfs/MTData/Ant_calibrations"

### paths to edi and png files if not already copied over
edi_path = r"/mnt/hgfs/MTData/GraniteSprings/granite_springs_edi"
png_path = r"/mnt/hgfs/MTData/GraniteSprings/granite_springs_plots"

### SCIENCE BASE 
### page id number
page_id = '5d5deee0e4b01d82ce9619c6'
username = 'jpeacock@usgs.gov'
password = None

### summarize all runs [ True | False ]
summarize = True

### upload data [ True | False]
upload_data = False 
upload_files = ['.zip', '.edi', '.png', '.xml', '.mth5']
#upload_files = ['.xml']
if upload_data:
    password = getpass.getpass()

# =============================================================================
# Make an archive folder to put everything
# =============================================================================
save_dir = os.path.join(station_dir, 'Archive')
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
# =============================================================================
# get station folders
# =============================================================================
station_list = [station for station in os.listdir(station_dir) if 
                os.path.isdir(os.path.join(station_dir, station))]

# =============================================================================
# Loop over stations
# =============================================================================
st = datetime.datetime.now()
for station in station_list:
    z3d_dir = os.path.join(station_dir, station)
    if os.path.isdir(z3d_dir):
        ### get the file names for each block of z3d files if none skip
        zc = archive.Z3DCollection()
        try:
            fn_list = zc.get_time_blocks(z3d_dir)
        except archive.ArchiveError:
            print('*** Skipping folder {0} because no Z3D files***'.format(station))
            continue
        
        ### make a folder in the archive folder
        station_save_dir = os.path.join(save_dir, station)
        if not os.path.exists(station_save_dir):
                os.mkdir(station_save_dir)
        print('--> Archiving Station {0} ...'.format(station))
        
        ### capture output to put into a log file
        with archive.Capturing() as output:
            station_st = datetime.datetime.now()
#            ### copy edi and png into archive director
#            if not os.path.isfile(os.path.join(station_save_dir, '{0}.edi'.format(station))):
#                shutil.copy(os.path.join(edi_path, '{0}.edi'.format(station)),
#                            os.path.join(station_save_dir, '{0}.edi'.format(station)))
#            if not os.path.isfile(os.path.join(station_save_dir, '{0}.png'.format(station))):
#                shutil.copy(os.path.join(png_path, '{0}.png'.format(station)),
#                            os.path.join(station_save_dir, '{0}.png'.format(station)))
                
            ### Make MTH5 File
            m = mth5.MTH5()
            mth5_fn = os.path.join(station_save_dir, '{0}.mth5'.format(station))
            m.open_mth5(mth5_fn)
            if not m.h5_is_write:
                raise mth5.MTH5Error('Something is wrong')
            
            ### update metadata from csv and cfg files
            m.update_metadata_from_cfg(cfg_fn) 
            if csv_fn is not None:
                try:
                    station_df = archive.get_station_info_from_csv(csv_fn,
                                                                   station)
                    m.update_metadata_from_series(station_df)
                except archive.ArchiveError as err:
                    print('{0} {1} {0}'.format('*'*4, err))
            m.write_metadata()
            
            ### loop over schedule blocks
            for ii, fn_block in enumerate(fn_list, 1):
                sch_obj = zc.merge_z3d(fn_block)
                sch_obj.name = 'schedule_{0:02}'.format(ii)
                sch_obj.write_metadata_csv(station_save_dir)
            
                ### create group for schedule action
                m.add_schedule(sch_obj)
                
            ### add calibrations
            for hh in ['hx', 'hy', 'hz']:
                mag_obj = getattr(m.field_notes, 'magnetometer_{0}'.format(hh))
                if mag_obj.id is not None and mag_obj.id != 0:
                    cal_fn = os.path.join(calibration_dir, 
                                          'ant_{0}.csv'.format(mag_obj.id))
                    cal_hx = mth5.Calibration()
                    cal_hx.from_csv(cal_fn)
                    cal_hx.name = hh
                    cal_hx.instrument_id = mag_obj.id
                    cal_hx.calibration_person.email = 'zonge@zonge.com'
                    cal_hx.calibration_person.name = 'Zonge International'
                    cal_hx.calibration_person.organization = 'Zonge International'
                    cal_hx.calibration_person.organization_url = 'zonge.com'
                    cal_hx.calibration_date = '2013-05-04'
                    cal_hx.units = 'mV/nT'
                    
                    m.add_calibration(cal_hx)
                
            m.close_mth5()
            ####------------------------------------------------------------------
            #### Make xml file for science base
            ####------------------------------------------------------------------
            # make a station database
            s_df, run_csv_fn = archive.combine_station_runs(station_save_dir)
            # summarize the runs
            s_df = archive.summarize_station_runs(s_df)
            # make xml file
            s_xml = sb_xml.XMLMetadata()
            s_xml.read_config_file(xml_cfg_fn)
            s_xml.supplement_info = s_xml.supplement_info.replace('\\n', '\n\t\t\t')
            
            # add station name to title
            s_xml.title += ', station {0}'.format(station)
            
            # location
            s_xml.survey.east = s_df.longitude
            s_xml.survey.west = s_df.longitude
            s_xml.survey.north = s_df.latitude
            s_xml.survey.south = s_df.latitude
            
            # get elevation from national map
            s_elev = archive.get_nm_elev(s_df.latitude, s_df.longitude) 
            s_xml.survey.elev_min = s_elev
            s_xml.survey.elev_max = s_elev
            
            # start and end time
            s_xml.survey.begin_date = s_df.start_date
            s_xml.survey.end_date = s_df.stop_date
            
            # add list of files
            s_xml.supplement_info += '\n\t\t\tFile List:\n\t\t\t'+'\n\t\t\t'.join(
                                    ['{0}.edi'.format(station),
                                     '{0}.png'.format(station),
                                     os.path.basename(mth5_fn)])
            
            # write station xml
            s_xml.write_xml_file(os.path.join(station_save_dir, 
                                              '{0}_meta.xml'.format(station)), 
                                write_station=True)
                
            station_et = datetime.datetime.now()
            t_diff = station_et-station_st
            print('Took --> {0:.2f} seconds'.format(t_diff.total_seconds()))
            
        ####------------------------------------------------------------------
        #### Upload data to science base
        #### -----------------------------------------------------------------
        if upload_data:
            try:
                archive.sb_upload_data(page_id, 
                                       station_save_dir, 
                                       username,
                                       password,
                                       f_types=upload_files)
            except Exception as error:
                print('xxx FAILED TO UPLOAD {0} xxx'.format(station))
                print(error)
                
            
        log_fn = os.path.join(station_save_dir,
                              'archive_{0}.log'.format(station))
        try:
            with open(log_fn, 'w') as log_fid:
                log_fid.write('\n'.join(output))
        except Exception as error:
            print('\tCould not write log file for {0}'.format(station))
            print(error)
            
# =============================================================================
# Combine all information into a database
# =============================================================================
if summarize:
    survey_df, survey_csv = archive.combine_survey_csv(save_dir)
    
    ### write shape file
    #shp_fn = archive.write_shp_file(survey_csv)
    
    ### write survey xml
    # adjust survey information to align with data 
    survey_xml = sb_xml.XMLMetadata()
    survey_xml.read_config_file(xml_cfg_fn)       
    survey_xml.supplement_info = survey_xml.supplement_info.replace('\\n', '\n\t\t\t')
    
    # location
    survey_xml.survey.east = survey_df.longitude.min()
    survey_xml.survey.west = survey_df.longitude.max()
    survey_xml.survey.south = survey_df.latitude.min()
    survey_xml.survey.north = survey_df.latitude.max()
    
    # get elevation min and max from station locations, not sure if this is correct
    survey_xml.survey.elev_min = survey_df.elevation.min()
    survey_xml.survey.elev_max = survey_df.elevation.max()
    
    # dates
    survey_xml.survey.begin_date = survey_df.start_date.min()
    survey_xml.survey.end_date = survey_df.stop_date.max()
    
    ### --> write survey xml file
    survey_xml.write_xml_file(os.path.join(save_dir, 
                                           '{0}.xml'.format('mp_survey')))

# print timing
et = datetime.datetime.now()
t_diff = et-st
print('--> Archiving took: {0}:{1:05.2f}, finished at {2}'.format(int(t_diff.total_seconds()//60),
                                              t_diff.total_seconds()%60,
                                              datetime.datetime.ctime(datetime.datetime.now())))

