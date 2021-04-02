# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 16:53:51 2018

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import os
import datetime
import mth5.mth5 as mth5
import usgs_archive.usgs_archive as archive
import usgs_archive.usgs_sb_xml as sb_xml

# =============================================================================
# Inputs
# =============================================================================
station_dir = r"d:\Peacock\MTData\MountainPass"
csv_fn = r"d:\Peacock\MTData\MountainPass\Archive\mp_survey_summary.csv"
cfg_fn = r"d:\Peacock\MTData\MountainPass\mp_mth5.cfg"
xml_cfg_fn = r"d:\Peacock\MTData\MountainPass\mp_archive.cfg"
calibration_dir = r"d:\Peacock\MTData\Ant_calibrations"
# =============================================================================
# Make an archive folder to put everything
# =============================================================================
save_dir = os.path.join(station_dir, "Archive")
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
# =============================================================================
# get station folders
# =============================================================================
station_list = [
    station
    for station in os.listdir(station_dir)
    if os.path.isdir(os.path.join(station_dir, station))
]

# =============================================================================
# Loop over stations
# =============================================================================
for station in station_list[6:7]:
    z3d_dir = os.path.join(station_dir, station)
    if os.path.isdir(z3d_dir):

        ### get the file names for each block of z3d files
        zc = archive.Z3DCollection()
        try:
            fn_list = zc.get_time_blocks(z3d_dir)
        except IndexError:
            print("*** Skipping folder {0} ***".format(station))
            continue

        ### make a folder in the archive folder
        station_save_dir = os.path.join(save_dir, station)
        if not os.path.exists(station_save_dir):
            os.mkdir(station_save_dir)

        st = datetime.datetime.now()
        ### Use with so that it will close if something goes amiss
        m = mth5.MTH5()
        mth5_fn = os.path.join(station_save_dir, "{0}.mth5".format(station))
        m.open_mth5(mth5_fn)
        if not m.h5_is_write:
            raise mth5.MTH5Error("Something is wrong")

        ### update metadata
        m.update_metadata_from_cfg(cfg_fn)
        m.update_metadata_from_series(
            archive.get_station_info_from_csv(csv_fn, station)
        )
        m.write_metadata()

        ### loop over schedule blocks
        for ii, fn_block in enumerate(fn_list, 1):
            sch_obj = zc.merge_z3d(fn_block)
            sch_obj.name = "schedule_{0:02}".format(ii)

            ### create group for schedule action
            m.add_schedule(sch_obj)

        ### add calibrations
        for hh in ["hx", "hy", "hz"]:
            mag_obj = getattr(m.field_notes, "magnetometer_{0}".format(hh))
            if mag_obj.id is not None:
                cal_fn = os.path.join(calibration_dir, "Ant_{0}.csv".format(mag_obj.id))
                cal_hx = mth5.Calibration()
                cal_hx.from_csv(cal_fn)
                cal_hx.name = hh
                cal_hx.calibration_person.email = "zonge@zonge.com"
                cal_hx.calibration_person.name = "Zonge International"
                cal_hx.calibration_person.organization = "Zonge Internationa"
                cal_hx.calibration_person.organization_url = "zonge.com"
                cal_hx.calibration_date = "2010-10-01"
                cal_hx.units = "mV/nT"

                m.add_calibration(cal_hx)

        m.close_mth5()

        ####------------------------------------------------------------------
        #### Make xml file for science base
        ####------------------------------------------------------------------
        # make a station database
        s_cfg = archive.USGScfg()
        s_db, csv_fn = s_cfg.combine_run_cfg(station_save_dir)
        # make xml file
        s_xml = sb_xml.XMLMetadata()
        s_xml.read_config_file(xml_cfg_fn)
        s_xml.supplement_info = s_xml.supplement_info.replace("\\n", "\n\t\t\t")

        # add station name to title
        s_xml.title += ", station {0}".format(station)

        # location
        s_xml.survey.east = s_db.lon.median()
        s_xml.survey.west = s_db.lon.median()
        s_xml.survey.north = s_db.lat.median()
        s_xml.survey.south = s_db.lat.median()

        # get elevation from national map
        s_elev = archive.get_nm_elev(s_db.lat.median(), s_db.lon.median())
        s_xml.survey.elev_min = s_elev
        s_xml.survey.elev_max = s_elev

        # start and end time
        s_xml.survey.begin_date = s_db.start_date.min()
        s_xml.survey.end_date = s_db.stop_date.max()

        # add list of files
        s_xml.supplement_info += "\n\t\t\tFile List:\n\t\t\t" + "\n\t\t\t".join(
            ["{0}.edi".format(station), "{0}".png.format(station), mth5_fn]
        )

        # write station xml
        s_xml.write_xml_file(
            os.path.join(station_save_dir, "{0}_meta.xml".format(station)),
            write_station=True,
        )

        et = datetime.datetime.now()
        t_diff = et - st
        print("Took --> {0:.2f} seconds".format(t_diff.total_seconds()))

    # return self.hdf5_fn
