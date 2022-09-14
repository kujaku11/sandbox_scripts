# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 14:38:59 2022

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path

from mtpy import MTCollection, MT
from mt_metadata.transfer_functions.tf import Survey, Station

# =============================================================================
general_survey = Survey()
general_survey.acquired_by.name = "Jared R. Peacock"
general_survey.acquired_by.organization = "U.S. Geological Survey"
general_survey.acquired_by.email = "jpeacock@usgs.gov"
general_survey.project = "CEC Geysers Monitoring"
general_survey.geographic_name = "The Geysers, CA"
general_survey.project_lead.email = "dalumbaugh@lbnl.gov"
general_survey.project_lead.organization = "Lawrence Berkeley National Lab"
general_survey.project_lead.name = "David Alumbaugh"
general_survey.country = "U.S.A."
general_survey.summary = (
    "Project funded by the California Energy Commission to monitor The Geysers "
    "with 3 annual repeat MT surveys and continous passive seismic.  Date "
    "will be joinlty inverted in 3D."
)
# =============================================================================
general_station = Station()
general_station.acquired_by.name = "Jared R. Peacock"
general_station.acquired_by.organization = "U.S. Geological Survey"
general_station.acquired_by.email = "jpeacock@usgs.gov"
general_station.location.declination.model = "IGRF"
general_station.orientation.method = "compass"
general_station.provenance.software.author = "Jared R. Peacock"
general_station.provenance.software.name = "MTpy"
general_station.provenance.software.version = "2.0.0"
general_station.transfer_function.sign_convention = "+"
general_station.transfer_function.units = (
    "millivolts per kilometer per nanotesla"
)


# =============================================================================
edi_path_2017 = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2017_EDI_files_birrp_processed\GeographicNorth"
)
edi_path_2021 = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2021_EDI_files_birrp_processed\GeographicNorth"
)
edi_path_2022 = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2022_EDI_files_birrp_processed\GeographicNorth"
)

# =============================================================================
mc = MTCollection(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC")
mc.open_collection(basename="cec_geysers_monitoring")

for edi_fn in edi_path_2017.glob("*.edi"):
    tf = MT(edi_fn)
    tf.read_tf_file()
    tf.survey_metadata.update(general_survey)
    tf.station_metadata.update(general_station)

    tf.survey_metadata.id = "GZ2017"
    tf.survey_metadata.name = "The Geysers MT Base Survey"

    tf.station = f"{tf.station[0:2]}3{tf.station[2:]}".lower()
    tf.station_metadata.location.declination.value = -13.86
    tf.station_metadata.time_period._end_dt = (
        tf.station_metadata.time_period._start_dt + (3600 * 25)
    )

    tf.station_metadata.runs[0].ex.type = "electric"
    tf.station_metadata.runs[0].ey.type = "electric"
    tf.station_metadata.runs[0].hy.measurement_azimuth = 90

    tf.station_metadata.runs[
        0
    ].ex.translated_azimuth = tf.station_metadata.location.declination.value
    tf.station_metadata.runs[
        0
    ].hx.translated_azimuth = tf.station_metadata.location.declination.value
    tf.station_metadata.runs[0].ey.translated_azimuth = (
        90 + tf.station_metadata.location.declination.value
    )
    tf.station_metadata.runs[0].hy.translated_azimuth = (
        90 + tf.station_metadata.location.declination.value
    )

    mc.add_tf(tf)

for edi_fn in edi_path_2021.glob("*.edi"):
    tf = MT(edi_fn)
    tf.read_tf_file()
    tf.survey_metadata.update(general_survey)
    tf.station_metadata.update(general_station)

    tf.survey_metadata.id = "GZ2021"
    tf.survey_metadata.name = "The Geysers MT Phase 1 Survey"

    if not tf.station.startswith("g"):
        tf.station = f"gz{tf.station}"
    tf.station_metadata.location.declination.value = -13.56
    tf.station_metadata.time_period._end_dt = (
        tf.station_metadata.time_period._start_dt + (3600 * 25)
    )

    tf.station_metadata.runs[0].ex.type = "electric"
    tf.station_metadata.runs[0].ey.type = "electric"
    tf.station_metadata.runs[0].hy.measurement_azimuth = 90

    tf.station_metadata.runs[
        0
    ].ex.translated_azimuth = tf.station_metadata.location.declination.value
    tf.station_metadata.runs[
        0
    ].hx.translated_azimuth = tf.station_metadata.location.declination.value
    tf.station_metadata.runs[0].ey.translated_azimuth = (
        90 + tf.station_metadata.location.declination.value
    )
    tf.station_metadata.runs[0].hy.translated_azimuth = (
        90 + tf.station_metadata.location.declination.value
    )

    mc.add_tf(tf)

for edi_fn in edi_path_2022.glob("*.edi"):
    tf = MT(edi_fn)
    tf.read_tf_file()
    tf.survey_metadata.update(general_survey)
    tf.station_metadata.update(general_station)

    tf.survey_metadata.id = "GZ2022"
    tf.survey_metadata.name = "The Geysers MT Pahse 2 Survey"

    tf.station_metadata.location.declination.value = -13.49
    tf.station_metadata.time_period._end_dt = (
        tf.station_metadata.time_period._start_dt + (3600 * 25)
    )

    tf.station_metadata.runs[0].hy.measurement_azimuth = 90
    tf.station_metadata.runs[
        0
    ].ex.translated_azimuth = tf.station_metadata.location.declination.value
    tf.station_metadata.runs[
        0
    ].hx.translated_azimuth = tf.station_metadata.location.declination.value
    tf.station_metadata.runs[0].ey.translated_azimuth = (
        90 + tf.station_metadata.location.declination.value
    )
    tf.station_metadata.runs[0].hy.translated_azimuth = (
        90 + tf.station_metadata.location.declination.value
    )

    mc.add_tf(tf)
