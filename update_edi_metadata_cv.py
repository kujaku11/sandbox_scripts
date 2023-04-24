# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 15:14:35 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import numpy as np
from mtpy import MT

# =============================================================================

edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\field_work\cv_edi_files_birrp\edited\GeographicNorth"
)

for edi_fn in edi_path.glob("*.edi"):
    m = MT()
    m.read_tf_file(edi_fn)

    # survey metadata
    m.survey_metadata.id = "CV2022"
    m.survey_metadata.project = "Great Basin Characterization"
    m.survey_metadata.geographic_name = "Clayton Valley, NV"
    m.survey_metadata.country = "USA"
    m.survey_metadata.state = "Nevada"

    # station metadata

    m.station_metadata.comments = ""
    m.station_metadata.runs = [m.station_metadata.runs[0]]

    m.station_metadata.acquired_by.author = (
        "U.S. Geological Survey: J. R. Peacock, B. Dean, S. Tarkany"
    )
    m.station_metadata.channel_layout = "L"
    m.station_metadata.comments = "measurement_coordinate_system = geomagnetic"
    m.station_metadata.data_type = "WBMT"
    m.station_metadata.runs[0].id = f"{edi_fn.stem}a"
    m.station_metadata.location.declination.comments = "from https://ngdc.noaa.gov/geomag/calculators/magcalc.shtml#declination "
    m.station_metadata.location.declination.model = "WMM"
    m.station_metadata.location.declination.value = 12.15
    m.station_metadata.orientation.method = "compass"
    m.station_metadata.orientation.reference_frame = "geographic"
    m.station_metadata.provenance.software.author = "Jared Peacock"
    m.station_metadata.provenance.software.name = "MTpy"
    m.station_metadata.provenance.software.version = "2.0.0"
    m.station_metadata.provenance.submitter.author = "Jared Peacock"
    m.station_metadata.provenance.submitter.email = "jpeacock@usgs.gov"
    m.station_metadata.provenance.submitter.organization = (
        "U.S. Geological Survey"
    )
    m.station_metadata.transfer_function.id = m.station
    m.station_metadata.transfer_function.runs_processed = [f"{edi_fn.stem}a"]
    m.station_metadata.transfer_function.coordinate_system = "geomagnetic"
    m.station_metadata.transfer_function.remote_references = []
    m.station_metadata.transfer_function.sign_convention = "+"
    m.station_metadata.transfer_function.units = (
        "millivolts_per_kilometer_per_nanotesla"
    )
    m.station_metadata.transfer_function.software.author = "A. Chave, WHOI"
    m.station_metadata.transfer_function.software.name = "BIRRP"
    m.station_metadata.transfer_function.version = "5.2.1"

    m.ex_metadata.channel_id = 4.0
    m.ex_metadata.channel_number = 4
    m.ex_metadata.contact_resistance.end = 2
    m.ex_metadata.contact_resistance.start = 2
    m.ex_metadata.measurement_azimuth = 0
    m.ex_metadata.dipole_length = 50
    m.ex_metadata.negative.manufacturer = "Borin"
    m.ex_metadata.negative.model = "Stelth 1"
    m.ex_metadata.negative.name = "Ag-AgCl"
    m.ex_metadata.positive.manufacturer = "Borin"
    m.ex_metadata.positive.model = "Stelth 1"
    m.ex_metadata.positive.name = "Ag-AgCl"
    m.ex_metadata.translated_azimuth = (
        -m.station_metadata.location.declination.value
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
    m.ey_metadata.dipole_length = 50
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
    m.hx_metadata.sensor.serial_number = ""
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
    m.hy_metadata.sensor.serial_number = ""
    m.hy_metadata.translated_azimuth = (
        m.hy_metadata.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    m.hy_metadata.translated_tilt = None
    m.hy_metadata.type = "magnetic"
    m.hy_metadata.units = "nanotesla"

    m.hz_metadata.measurement_azimuth = 0
    m.hz_metadata.measurement_tilt = 90
    m.hz_metadata.sensor.manufacturer = "Zonge International"
    m.hz_metadata.sensor.model = "ANT4"
    m.hz_metadata.sensor.type = "magnetic induction coil"
    m.hz_metadata.translated_azimuth = 0
    m.hz_metadata.translated_tilt = 90
    m.hz_metadata.type = "magnetic"
    m.hz_metadata.units = "nanotesla"

    m.write_tf_file(
        save_dir=r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\field_work\cv_edi_files_birrp\edited\GeographicNorth\updated"
    )
