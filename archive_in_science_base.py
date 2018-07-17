# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 12:55:59 2018

@author: jpeacock
"""
import os
import mtpy.usgs.usgs_archive as archive

# =============================================================================
# Inputs
# =============================================================================
survey_dir = r"/mnt/hgfs/MTData/iMUSH_Zen_samples/imush"
survey_cfg = r"/mnt/hgfs/MTData/iMUSH_Zen_samples/imush_archive.cfg"
survey = 'iMUSH'

save_dir = os.path.join(survey_dir, 'Archive')
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
# =============================================================================
# make the survey xml file
# =============================================================================
survey_xml = archive.XMLMetadata()
survey_xml.read_config_file(survey_cfg)

for station in os.listdir(survey_dir)[2:]:
    station_path = os.path.join(survey_dir, station)
    station_save_dir = os.path.join(save_dir, station)
    
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
        asc_fn_list = ['{0}{1}'.format(station.upper(), ext) for ext in 
                       ['_meta.xml', '.edi', '.png']]
        for fn_block in fn_list:
            zm.get_z3d_db(fn_block)
            zm.read_mtft24_cfg()
            zm.CoordinateSystem = 'Geomagnetic North'
            zm.SurveyID = survey
            zm.write_asc_file(save_dir=station_save_dir,
                              full=False, compress=True)
            asc_fn_list.append(zm._make_file_name(save_path=station_save_dir, 
                                                  compression=True))
            zm.write_station_info_metadata(save_dir=station_save_dir)
            
        # make a station database
        s_cfg = archive.USGScfg()
        s_db, csv_fn = s_cfg.combine_run_cfg(station_save_dir)
        
        # make xml file
        s_xml = archive.XMLMetadata()
        s_xml.read_config_file(survey_cfg)
        
        # location
        s_xml.survey.east = s_db.lon.median()
        s_xml.survey.west = s_db.lon.median()
        s_xml.survey.north = s_db.lat.median()
        s_xml.survey.south = s_db.lat.median()
        
        s_elev = archive.get_nm_elev(s_db.lat.median(), s_db.lon.median()) 
        s_xml.survey.elev_min = s_elev
        s_xml.survey.elev_max = s_elev
        
        # start and end time
        s_xml.survey.begin_date = s_db.start_date.min()
        s_xml.survey.end_date = s_db.stop_date.max()
        
        # add list of files
        s_xml.supplement_info += '\n\t\t\tFile List:\n\t\t\t'+'\n\t\t\t'.join(asc_fn_list)
        
        # write station xml
        s_xml.write_xml_file(os.path.join(station_save_dir, 
                                          '{0}_meta.xml'.format(station.upper())))

# adjust survey information to align with data        
survey_cfg = archive.USGScfg()
survey_db, csv_fn = survey_cfg.combine_all_station_info(save_dir)

# location
survey_xml.survey.east = survey_db.lon.min()
survey_xml.survey.west = survey_db.lon.max()
survey_xml.survey.south = survey_db.lat.min()
survey_xml.survey.north = survey_db.lat.max()

# dates
survey_xml.survey.begin_date = survey_db.start_date.min()
survey_xml.survey.end_date = survey_db.stop_date.max()

survey_xml.write_xml_file(os.path.join(save_dir, 
                                       '{0}.xml'.format(survey)))
        
