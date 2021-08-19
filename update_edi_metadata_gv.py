# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 18:02:58 2021

@author: jpeacock
"""
from pathlib import Path
import pandas as pd
import numpy as np
from mtpy.core.mt import MT

survey_csv_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\gv_survey_summary.csv"
# edi_fn = r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\gv160.edi"

# test_fn = Path(r"c:\Users\jpeacock\Documents\GitHub\sandbox_scripts\test.edi")
# if test_fn.exists():
#     test_fn.unlink()
edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES")
edi_list = [edi_path.joinpath(f"gv{ii:03}.edi") for ii in range(100, 170)]
                
for edi_fn in edi_list:
    if not edi_fn.is_file():
        continue               

    m = MT(fn=edi_fn)
    
    survey_df = pd.read_csv(survey_csv_fn)
    sdf = [entry for entry in survey_df.loc[survey_df.station == m. station].itertuples()][0]
    
    # survey
    m.survey_metadata.acquired_by.author = "Jared R. Peacock"
    m.survey_metadata.acquired_by.comments = "U.S. Geological Survey"
    m.survey_metadata.citation_dataset.authors = "J. R. Peacock, D. L. Siler, B. Dean, L. Zielinski"
    m.survey_metadata.citation_dataset.doi = "https://doi.org/10.5066/P9GZ9Z56"
    m.survey_metadata.citation_dataset.year = "2020"
    m.survey_metadata.comments = None
    m.survey_metadata.country = "USA"
    m.survey_metadata.datum = "WGS84"
    m.survey_metadata.geographic_name = "Gabbs Valley"
    m.survey_metadata.name = "Shark Tank Gabbs Valley"
    m.survey_metadata.northwest_corner.latitude = 0.0
    m.survey_metadata.northwest_corner.longitude = 0.0
    m.survey_metadata.project = "Energy Resources Program"
    m.survey_metadata.project_lead.author = "J. R. Peacock"
    m.survey_metadata.project_lead.email = "jpeacock@usgs.gov"
    m.survey_metadata.project_lead.organization = "U. S. Geological Survey"
    m.survey_metadata.release_license = "CC-0"
    m.survey_metadata.southeast_corner.latitude = 0.0
    m.survey_metadata.southeast_corner.longitude = 0.0
    m.survey_metadata.summary = (
        "A 1-year project to demonstrate the need for full crustal imaging to"
        " understand geothermal and mineral systems")
    m.survey_metadata.id = "GV2020"
    m.survey_metadata.time_period.end_date = "2020-08-01"
    m.survey_metadata.time_period.start_date = "2020-09-30"
    
    # Station
    m.station_metadata.acquired_by.author = "Jared Peacock"
    m.station_metadata.acquired_by.comments = "U.S. Geological Survey"
    m.station_metadata.channel_layout = "L"
    m.station_metadata.comments = "measurement_coordinate_system = geomagnetic"
    m.station_metadata.data_type = "WBMT"
    m.station_metadata.location.declination.comments = "from https://ngdc.noaa.gov/geomag/calculators/magcalc.shtml#declination "
    m.station_metadata.location.declination.model = "WMM"
    m.station_metadata.location.declination.value = 12.5
    m.station_metadata.orientation.method = "compass"
    m.station_metadata.orientation.reference_frame = "geographic"
    m.station_metadata.provenance.comments = "Archived on Science Base https://doi.org/10.5066/P9GZ9Z56"
    m.station_metadata.provenance.software.author = "Jared Peacock"
    m.station_metadata.provenance.software.name = "MTpy"
    m.station_metadata.provenance.software.version = "metadata branch"
    m.station_metadata.provenance.submitter.author = "Jared Peacock"
    m.station_metadata.provenance.submitter.email = "jpeacock@usgs.gov"
    m.station_metadata.provenance.submitter.organization = "U.S. Geological Survey"
    m.station_metadata.transfer_function.processed_date = "2020-10-01"
    m.station_metadata.transfer_function.processing_parameters = []
    m.station_metadata.transfer_function.remote_references = []
    m.station_metadata.transfer_function.sign_convention = "+"
    m.station_metadata.transfer_function.units = "millivolts_per_kilometer_per_nanotesla"
    
    
    m.ex_metadata.channel_id = 4.0
    m.ex_metadata.channel_number = 4
    m.ex_metadata.contact_resistance.end = sdf.ex_cres_start
    m.ex_metadata.contact_resistance.start = sdf.ex_cres_end
    m.ex_metadata.measurement_azimuth = sdf.ex_azimuth
    m.ex_metadata.dipole_length = sdf.ex_length
    m.ex_metadata.negative.manufacturer = "Borin"
    m.ex_metadata.negative.model = "Stelth 1"
    m.ex_metadata.negative.name = "Ag-AgCl"
    m.ex_metadata.positive.manufacturer = "Borin"
    m.ex_metadata.positive.model = "Stelth 1"
    m.ex_metadata.positive.name = "Ag-AgCl"
    m.ex_metadata.translated_azimuth = m.ex_metadata.measurement_azimuth - m.station_metadata.location.declination.value
    m.ex_metadata.positive.x = 0
    m.ex_metadata.positive.x2 = m.ex_metadata.dipole_length * np.cos(np.deg2rad(m.ex_metadata.translated_azimuth))
    m.ex_metadata.positive.y = 0
    m.ex_metadata.positive.y2 = m.ex_metadata.dipole_length * np.sin(np.deg2rad(m.ex_metadata.translated_azimuth))
    m.ex_metadata.units = "millivolts"
    m.ex_metadata.type = "electric"
    
    m.ey_metadata.channel_id = 5.0
    m.ey_metadata.channel_number = 5
    m.ey_metadata.contact_resistance.end = sdf.ey_cres_start
    m.ey_metadata.contact_resistance.start = sdf.ey_cres_end
    m.ey_metadata.measurement_azimuth = sdf.ey_azimuth
    m.ey_metadata.dipole_length = sdf.ey_length
    m.ey_metadata.negative.manufacturer = "Borin"
    m.ey_metadata.negative.model = "Stelth 1"
    m.ey_metadata.negative.name = "Ag-AgCl"
    m.ey_metadata.positive.manufacturer = "Borin"
    m.ey_metadata.positive.model = "Stelth 1"
    m.ey_metadata.positive.name = "Ag-AgCl"
    m.ey_metadata.translated_azimuth = m.ey_metadata.measurement_azimuth - m.station_metadata.location.declination.value
    m.ey_metadata.positive.x = 0
    m.ey_metadata.positive.x2 = m.ey_metadata.dipole_length * np.cos(np.deg2rad(m.ey_metadata.translated_azimuth))
    m.ey_metadata.positive.y = 0
    m.ey_metadata.positive.y2 = m.ey_metadata.dipole_length * np.sin(np.deg2rad(m.ey_metadata.translated_azimuth))
    m.ey_metadata.units = "millivolts"
    m.ey_metadata.type = "electric"
    
    m.hx_metadata.measurement_azimuth = sdf.hx_azimuth
    m.hx_metadata.measurement_tilt = 0.0
    m.hx_metadata.sensor.manufacturer = "Zonge International"
    m.hx_metadata.sensor.model = "ANT4"
    m.hx_metadata.sensor.type = "magnetic induction coil"
    m.hx_metadata.translated_azimuth = m.hx_metadata.measurement_azimuth - m.station_metadata.location.declination.value
    m.hx_metadata.translated_tilt = None
    m.hx_metadata.type = "magnetic"
    m.hx_metadata.units = "nanotesla"
    
    m.hy_metadata.measurement_azimuth = sdf.hy_azimuth
    m.hy_metadata.measurement_tilt = 0.0
    m.hy_metadata.sensor.manufacturer = "Zonge International"
    m.hy_metadata.sensor.model = "ANT4"
    m.hy_metadata.sensor.type = "magnetic induction coil"
    m.hy_metadata.translated_azimuth = m.hy_metadata.measurement_azimuth - m.station_metadata.location.declination.value
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
    
    
    m.write_mt_file()