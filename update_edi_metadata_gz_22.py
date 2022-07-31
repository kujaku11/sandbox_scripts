# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 18:02:58 2021

@author: jpeacock
"""
from pathlib import Path
import pandas as pd
import numpy as np
from mtpy.core.mt import MT

survey_csv_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2022_EDI_files_birrp_processed\gz_2022_survey_summary.csv"

# test_fn = Path(r"c:\Users\jpeacock\Documents\GitHub\sandbox_scripts\test.edi")
# if test_fn.exists():
#     test_fn.unlink()
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2022_EDI_files_birrp_processed"
)
edi_list = list(edi_path.glob("*.edi"))
survey_df = pd.read_csv(survey_csv_fn)
survey_df.start = pd.to_datetime(survey_df.start)

for edi_fn in edi_list:
    if not edi_fn.is_file():
        continue

    m = MT(fn=edi_fn)
    m.station = edi_fn.stem

    sdf = survey_df.loc[survey_df.station == int(m.station[2:])]
    lat = sdf.latitude.mean()
    lon = sdf.longitude.mean()
    elev = sdf.elevation.mean()
    start = sdf.start.min().isoformat()
    end = (sdf.start.max() + np.timedelta64(3, "h")).isoformat()
    ex_length = sdf.loc[sdf.component == "ex"].dipole_length.mean()
    ey_length = sdf.loc[sdf.component == "ey"].dipole_length.mean()
    hx_sensor = sdf.loc[sdf.component == "hx"].coil_number.mean()
    hy_sensor = sdf.loc[sdf.component == "hy"].coil_number.mean()
    hz_sensor = sdf.loc[sdf.component == "hz"].coil_number.mean()

    # survey
    m.survey_metadata.acquired_by.author = "Jared R. Peacock"
    m.survey_metadata.acquired_by.comments = "U.S. Geological Survey"
    m.survey_metadata.citation_dataset.authors = (
        "J. R. Peacock, D. Alumbaugh, M. A. Mitchell"
    )
    m.survey_metadata.citation_dataset.doi = ""
    m.survey_metadata.citation_dataset.year = "2022"
    m.survey_metadata.comments = None
    m.survey_metadata.country = "USA"
    m.survey_metadata.datum = "WGS84"
    m.survey_metadata.geographic_name = "The Geysers"
    m.survey_metadata.name = "The Geysers Phase 2"
    m.survey_metadata.northwest_corner.latitude = survey_df.latitude.max()
    m.survey_metadata.northwest_corner.longitude = survey_df.longitude.max()
    m.survey_metadata.project = "The Geysers Monitoring"
    m.survey_metadata.project_lead.author = "J. R. Peacock"
    m.survey_metadata.project_lead.email = "jpeacock@usgs.gov"
    m.survey_metadata.project_lead.organization = "U. S. Geological Survey"
    m.survey_metadata.release_license = "CC-0"
    m.survey_metadata.southeast_corner.latitude = survey_df.latitude.min()
    m.survey_metadata.southeast_corner.longitude = survey_df.longitude.min()
    m.survey_metadata.summary = "2nd of 3 repeat MT measurements at The Geysers to monitor the steam field"
    m.survey_metadata.id = "GZ2022"
    m.survey_metadata.time_period.end_date = (
        (survey_df.start.max() + np.timedelta64(1, "D")).date().isoformat()
    )
    m.survey_metadata.time_period.start_date = (
        survey_df.start.min().date().isoformat()
    )

    # Station
    m.station_metadata.acquired_by.author = "Jared Peacock"
    m.station_metadata.acquired_by.comments = "U.S. Geological Survey"
    m.station_metadata.time_period.start = start
    m.station_metadata.channel_layout = "L"
    m.station_metadata.comments = "measurement_coordinate_system = geomagnetic"
    m.station_metadata.data_type = "WBMT"
    m.station_metadata.runs[0].id = f"{edi_fn.stem}a"
    m.station_metadata.location.declination.comments = "from https://ngdc.noaa.gov/geomag/calculators/magcalc.shtml#declination "
    m.station_metadata.location.declination.model = "WMM"
    m.station_metadata.location.declination.value = 13.43
    m.station_metadata.location.latitude = lat
    m.station_metadata.location.longitude = lon
    m.station_metadata.location.elevation = elev
    m.station_metadata.orientation.method = "compass"
    m.station_metadata.orientation.reference_frame = "geographic"
    m.station_metadata.provenance.comments = "Archived on Science Base ..."
    m.station_metadata.provenance.software.author = "Jared Peacock"
    m.station_metadata.provenance.software.name = "MTpy"
    m.station_metadata.provenance.software.version = "metadata branch"
    m.station_metadata.provenance.submitter.author = "Jared Peacock"
    m.station_metadata.provenance.submitter.email = "jpeacock@usgs.gov"
    m.station_metadata.provenance.submitter.organization = (
        "U.S. Geological Survey"
    )
    m.station_metadata.transfer_function.id = edi_fn.stem
    m.station_metadata.transfer_function.runs_processed = [f"{edi_fn.stem}a"]
    m.station_metadata.transfer_function.processed_date = "2022-5-01"
    m.station_metadata.transfer_function.coordinate_system = "geomagnetic"
    m.station_metadata.transfer_function.processing_parameters = []
    m.station_metadata.transfer_function.remote_references = []
    m.station_metadata.transfer_function.sign_convention = "+"
    m.station_metadata.transfer_function.units = (
        "millivolts_per_kilometer_per_nanotesla"
    )

    m.ex_metadata.channel_id = 4.0
    m.ex_metadata.channel_number = 4
    m.ex_metadata.contact_resistance.end = 2
    m.ex_metadata.contact_resistance.start = 2
    m.ex_metadata.measurement_azimuth = 0
    m.ex_metadata.dipole_length = ex_length
    m.ex_metadata.negative.manufacturer = "Borin"
    m.ex_metadata.negative.model = "Stelth 1"
    m.ex_metadata.negative.name = "Ag-AgCl"
    m.ex_metadata.positive.manufacturer = "Borin"
    m.ex_metadata.positive.model = "Stelth 1"
    m.ex_metadata.positive.name = "Ag-AgCl"
    m.ex_metadata.translated_azimuth = (
        m.ex_metadata.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    m.ex_metadata.positive.x = 0
    m.ex_metadata.positive.x2 = m.ex_metadata.dipole_length * np.cos(
        np.deg2rad(m.ex_metadata.translated_azimuth)
    )
    m.ex_metadata.positive.y = 0
    m.ex_metadata.positive.y2 = m.ex_metadata.dipole_length * np.sin(
        np.deg2rad(m.ex_metadata.translated_azimuth)
    )
    m.ex_metadata.units = "millivolts"
    m.ex_metadata.type = "electric"

    m.ey_metadata.channel_id = 5.0
    m.ey_metadata.channel_number = 5
    m.ey_metadata.contact_resistance.end = 2
    m.ey_metadata.contact_resistance.start = 2
    m.ey_metadata.measurement_azimuth = 90
    m.ey_metadata.dipole_length = ey_length
    m.ey_metadata.negative.manufacturer = "Borin"
    m.ey_metadata.negative.model = "Stelth 1"
    m.ey_metadata.negative.name = "Ag-AgCl"
    m.ey_metadata.positive.manufacturer = "Borin"
    m.ey_metadata.positive.model = "Stelth 1"
    m.ey_metadata.positive.name = "Ag-AgCl"
    m.ey_metadata.translated_azimuth = (
        m.ey_metadata.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    m.ey_metadata.positive.x = 0
    m.ey_metadata.positive.x2 = m.ey_metadata.dipole_length * np.cos(
        np.deg2rad(m.ey_metadata.translated_azimuth)
    )
    m.ey_metadata.positive.y = 0
    m.ey_metadata.positive.y2 = m.ey_metadata.dipole_length * np.sin(
        np.deg2rad(m.ey_metadata.translated_azimuth)
    )
    m.ey_metadata.units = "millivolts"
    m.ey_metadata.type = "electric"

    m.hx_metadata.measurement_azimuth = 0
    m.hx_metadata.measurement_tilt = 0.0
    m.hx_metadata.sensor.manufacturer = "Zonge International"
    m.hx_metadata.sensor.model = "ANT4"
    m.hx_metadata.sensor.type = "magnetic induction coil"
    m.hx_metadata.sensor.serial_number = hx_sensor
    m.hx_metadata.translated_azimuth = (
        m.hx_metadata.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    m.hx_metadata.translated_tilt = None
    m.hx_metadata.type = "magnetic"
    m.hx_metadata.units = "nanotesla"

    m.hy_metadata.measurement_azimuth = 90
    m.hy_metadata.measurement_tilt = 0.0
    m.hy_metadata.sensor.manufacturer = "Zonge International"
    m.hy_metadata.sensor.model = "ANT4"
    m.hy_metadata.sensor.type = "magnetic induction coil"
    m.hy_metadata.sensor.serial_number = hy_sensor
    m.hy_metadata.translated_azimuth = (
        m.hy_metadata.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    m.hy_metadata.translated_tilt = None
    m.hy_metadata.type = "magnetic"
    m.hy_metadata.units = "nanotesla"

    # m.hz_metadata.measurement_azimuth = 0
    # m.hz_metadata.measurement_tilt = 90
    # m.hz_metadata.sensor.manufacturer = "Zonge International"
    # m.hz_metadata.sensor.model = "ANT4"
    # m.hz_metadata.sensor.type = "magnetic induction coil"
    # m.hz_metadata.translated_azimuth = 0
    # m.hz_metadata.translated_tilt = 90
    # m.hz_metadata.type = "magnetic"
    # m.hz_metadata.units = "nanotesla"
    m.write_tf_file(
        save_dir=r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2022_EDI_files_birrp_processed\updated"
    )
