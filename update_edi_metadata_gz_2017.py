# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 18:02:58 2021

@author: jpeacock
"""
from pathlib import Path
import pandas as pd
import numpy as np
from mtpy.core.mt import MT

survey_csv_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2017_EDI_files_birrp_processed\gz_2017_survey_summary.csv"

# test_fn = Path(r"c:\Users\jpeacock\Documents\GitHub\sandbox_scripts\test.edi")
# if test_fn.exists():
#     test_fn.unlink()
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\2017_EDI_files_birrp_processed\GeographicNorth"
)
edi_list = list(edi_path.glob("*.edi"))
survey_df = pd.read_csv(survey_csv_fn)
survey_df.start = pd.to_datetime(survey_df.start)

for edi_fn in edi_list:
    if not edi_fn.is_file():
        continue

    m = MT(fn=edi_fn)
    m.read()
    m.station_metadata.remove_run("001")
    m.station_metadata.comments = ""

    sdf = survey_df.loc[survey_df.station == edi_fn.stem]

    m.station = f"gz3{edi_fn.stem[-2:]}"
    lat = sdf.latitude.mean()
    lon = sdf.longitude.mean()
    elev = sdf.elevation.mean()
    start = sdf.start.min().isoformat()
    end = (sdf.start.max() + np.timedelta64(3, "h")).isoformat()
    ex_length = sdf.loc[sdf.component == "ex"].dipole.mean()
    ey_length = sdf.loc[sdf.component == "ey"].dipole.mean()
    hx_sensor = sdf.loc[sdf.component == "hx"].coil_number.mean()
    hy_sensor = sdf.loc[sdf.component == "hy"].coil_number.mean()
    # hz_sensor = sdf.loc[sdf.component == "hz"].coil_number.mean()

    # survey
    m.survey_metadata.comments = ""
    m.survey_metadata.acquired_by.author = "Jared R. Peacock"
    m.survey_metadata.acquired_by.comments = "U.S. Geological Survey"
    m.survey_metadata.citation_dataset.authors = (
        "J. R. Peacock, M. T. Mangan, M. Walters, C. Hartline"
    )
    m.survey_metadata.citation_dataset.doi = ""
    m.survey_metadata.citation_dataset.year = "2017"
    m.survey_metadata.comments = None
    m.survey_metadata.country = "USA"
    m.survey_metadata.datum = "WGS84"
    m.survey_metadata.geographic_name = "The Geysers"
    m.survey_metadata.name = "The Geysers Original Survey"
    m.survey_metadata.northwest_corner.latitude = survey_df.latitude.max()
    m.survey_metadata.northwest_corner.longitude = survey_df.longitude.max()
    m.survey_metadata.project = "MT Imaging of The Geysers"
    m.survey_metadata.project_lead.author = "J. R. Peacock"
    m.survey_metadata.project_lead.email = "jpeacock@usgs.gov"
    m.survey_metadata.project_lead.organization = "U. S. Geological Survey"
    m.survey_metadata.release_license = "CC-0"
    m.survey_metadata.southeast_corner.latitude = survey_df.latitude.min()
    m.survey_metadata.southeast_corner.longitude = survey_df.longitude.min()
    m.survey_metadata.summary = "Imaging The Geysers steam field with MT"
    m.survey_metadata.id = "GZ2017"
    m.survey_metadata.time_period.end_date = (
        (survey_df.start.max() + np.timedelta64(1, "D")).date().isoformat()
    )
    m.survey_metadata.time_period.start_date = (
        survey_df.start.min().date().isoformat()
    )

    # Station
    m.station_metadata.comments = ""
    m.station_metadata.acquired_by.author = "Jared Peacock"
    m.station_metadata.acquired_by.comments = "U.S. Geological Survey"
    m.station_metadata.time_period.start = start
    m.station_metadata.channel_layout = "L"
    m.station_metadata.comments = "measurement_coordinate_system = geomagnetic"
    m.station_metadata.data_type = "WBMT"
    m.station_metadata.runs[0].id = f"{edi_fn.stem}a"
    m.station_metadata.location.declination.comments = "from https://ngdc.noaa.gov/geomag/calculators/magcalc.shtml#declination "
    m.station_metadata.location.declination.model = "WMM"
    m.station_metadata.location.declination.value = 14.2
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
    m.station_metadata.transfer_function.id = m.station
    m.station_metadata.transfer_function.runs_processed = [f"{edi_fn.stem}a"]
    m.station_metadata.transfer_function.processed_date = "2017-07-30"
    m.station_metadata.transfer_function.coordinate_system = "geographic"
    m.station_metadata.transfer_function.processing_parameters = []
    m.station_metadata.transfer_function.remote_references = [
        "local synchronous stations",
    ]
    m.station_metadata.transfer_function.sign_convention = "+"
    m.station_metadata.transfer_function.units = (
        "millivolts_per_kilometer_per_nanotesla"
    )

    ### EX
    m.station_metadata.runs[0].ex.channel_id = 4.0
    m.station_metadata.runs[0].ex.channel_number = 4
    m.station_metadata.runs[0].ex.contact_resistance.end = 2
    m.station_metadata.runs[0].ex.contact_resistance.start = 2
    m.station_metadata.runs[0].ex.measurement_azimuth = 0
    m.station_metadata.runs[0].ex.dipole_length = ex_length
    m.station_metadata.runs[0].ex.negative.manufacturer = "Borin"
    m.station_metadata.runs[0].ex.negative.model = "Stelth 1"
    m.station_metadata.runs[0].ex.negative.name = "Ag-AgCl"
    m.station_metadata.runs[0].ex.positive.manufacturer = "Borin"
    m.station_metadata.runs[0].ex.positive.model = "Stelth 1"
    m.station_metadata.runs[0].ex.positive.name = "Ag-AgCl"
    m.station_metadata.runs[0].ex.translated_azimuth = (
        m.station_metadata.runs[0].ex.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    m.station_metadata.runs[0].ex.positive.x = 0
    m.station_metadata.runs[0].ex.positive.x2 = m.station_metadata.runs[
        0
    ].ex.dipole_length * np.cos(
        np.deg2rad(m.station_metadata.runs[0].ex.translated_azimuth)
    )
    m.station_metadata.runs[0].ex.positive.y = 0
    m.station_metadata.runs[0].ex.positive.y2 = m.station_metadata.runs[
        0
    ].ex.dipole_length * np.sin(
        np.deg2rad(m.station_metadata.runs[0].ex.translated_azimuth)
    )
    m.station_metadata.runs[0].ex.units = "millivolts"
    m.station_metadata.runs[0].ex.type = "electric"

    ### EY
    m.station_metadata.runs[0].ey.channel_id = 5.0
    m.station_metadata.runs[0].ey.channel_number = 5
    m.station_metadata.runs[0].ey.contact_resistance.end = 2
    m.station_metadata.runs[0].ey.contact_resistance.start = 2
    m.station_metadata.runs[0].ey.measurement_azimuth = 90
    m.station_metadata.runs[0].ey.dipole_length = ey_length
    m.station_metadata.runs[0].ey.negative.manufacturer = "Borin"
    m.station_metadata.runs[0].ey.negative.model = "Stelth 1"
    m.station_metadata.runs[0].ey.negative.name = "Ag-AgCl"
    m.station_metadata.runs[0].ey.positive.manufacturer = "Borin"
    m.station_metadata.runs[0].ey.positive.model = "Stelth 1"
    m.station_metadata.runs[0].ey.positive.name = "Ag-AgCl"
    m.station_metadata.runs[0].ey.translated_azimuth = (
        m.station_metadata.runs[0].ey.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    m.station_metadata.runs[0].ey.positive.x = 0
    m.station_metadata.runs[0].ey.positive.x2 = m.station_metadata.runs[
        0
    ].ey.dipole_length * np.cos(
        np.deg2rad(m.station_metadata.runs[0].ey.translated_azimuth)
    )
    m.station_metadata.runs[0].ey.positive.y = 0
    m.station_metadata.runs[0].ey.positive.y2 = m.station_metadata.runs[
        0
    ].ey.dipole_length * np.sin(
        np.deg2rad(m.station_metadata.runs[0].ey.translated_azimuth)
    )
    m.station_metadata.runs[0].ey.units = "millivolts"
    m.station_metadata.runs[0].ey.type = "electric"

    ### HX
    m.station_metadata.runs[0].hx.channel_id = 1.0
    m.station_metadata.runs[0].hx.measurement_azimuth = 0
    m.station_metadata.runs[0].hx.measurement_tilt = 0.0
    m.station_metadata.runs[0].hx.sensor.manufacturer = "Zonge International"
    m.station_metadata.runs[0].hx.sensor.model = "ANT4"
    m.station_metadata.runs[0].hx.sensor.type = "magnetic induction coil"
    m.station_metadata.runs[0].hx.sensor.serial_number = hx_sensor
    m.station_metadata.runs[0].hx.translated_azimuth = (
        m.station_metadata.runs[0].hx.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    m.station_metadata.runs[0].hx.translated_tilt = None
    m.station_metadata.runs[0].hx.type = "magnetic"
    m.station_metadata.runs[0].hx.units = "nanotesla"

    ### HY
    m.station_metadata.runs[0].hy.channel_id = 2.0
    m.station_metadata.runs[0].hy.measurement_azimuth = 90
    m.station_metadata.runs[0].hy.measurement_tilt = 0.0
    m.station_metadata.runs[0].hy.sensor.manufacturer = "Zonge International"
    m.station_metadata.runs[0].hy.sensor.model = "ANT4"
    m.station_metadata.runs[0].hy.sensor.type = "magnetic induction coil"
    m.station_metadata.runs[0].hy.sensor.serial_number = hy_sensor
    m.station_metadata.runs[0].hy.translated_azimuth = (
        m.station_metadata.runs[0].hy.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    m.station_metadata.runs[0].hy.translated_tilt = None
    m.station_metadata.runs[0].hy.type = "magnetic"
    m.station_metadata.runs[0].hy.units = "nanotesla"

    ### HZ
    # m.station_metadata.runs[0].hz.measurement_azimuth = 0
    # m.station_metadata.runs[0].hz.measurement_tilt = 90
    # m.station_metadata.runs[0].hz.sensor.manufacturer = "Zonge International"
    # m.station_metadata.runs[0].hz.sensor.model = "ANT4"
    # m.station_metadata.runs[0].hz.sensor.type = "magnetic induction coil"
    # m.station_metadata.runs[0].hz.translated_azimuth = 0
    # m.station_metadata.runs[0].hz.translated_tilt = 90
    # m.station_metadata.runs[0].hz.type = "magnetic"
    # m.station_metadata.runs[0].hz.units = "nanotesla"

    for ch in ["hz", "rrhx", "rrhy"]:
        m.station_metadata.runs[0].remove_channel(ch)

    edi_obj = m.write(save_dir=edi_path.joinpath("updated"))
