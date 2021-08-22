# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 18:02:58 2021

@author: jpeacock
"""

from mtpy.core.mt import MT

edi_fn = r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\gv160.edi"

m = MT(fn=edi_fn)

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
m.station_metadata.comments = ""
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
m.station_metadata.time_period.start = "2020-08-16T00:00:00+00:00"
m.station_metadata.transfer_function.processed_date = "2020-10-01"
m.station_metadata.transfer_function.processing_parameters = []
m.station_metadata.transfer_function.remote_references = []
m.station_metadata.transfer_function.runs_processed = ['gv160a']
m.station_metadata.transfer_function.sign_convention = "+"
m.station_metadata.transfer_function.units = "millivolts_per_kilometer_per_nanotesla"


m.ex_metadata.channel_id = 4.0
m.ex_metadata.channel_number = 4
m.ex_metadata.contact_resistance.end = None
m.ex_metadata.contact_resistance.start = None
m.ex_metadata.data_quality.flag = 0
m.ex_metadata.data_quality.good_from_period = None
m.ex_metadata.data_quality.good_to_period = None
m.ex_metadata.data_quality.rating.author = None
m.ex_metadata.data_quality.rating.method = None
m.ex_metadata.data_quality.rating.value = 0
m.ex_metadata.data_quality.warnings = None
m.ex_metadata.dc.end = None
m.ex_metadata.dc.start = None
m.ex_metadata.dipole_length = 56.0
m.ex_metadata.filter.applied = [False]
m.ex_metadata.filter.comments = None
m.ex_metadata.filter.name = ['none']
m.ex_metadata.measurement_azimuth = 0.0
m.ex_metadata.measurement_tilt = 0.0
m.ex_metadata.negative.elevation = 0.0
m.ex_metadata.negative.id = None
m.ex_metadata.negative.latitude = 0.0
m.ex_metadata.negative.longitude = 0.0
m.ex_metadata.negative.manufacturer = None
m.ex_metadata.negative.model = None
m.ex_metadata.negative.name = None
m.ex_metadata.negative.settings = None
m.ex_metadata.negative.type = electric
m.ex_metadata.negative.x = 0.0
m.ex_metadata.negative.x2 = 0.0
m.ex_metadata.negative.y = 0.0
m.ex_metadata.negative.y2 = 0.0
m.ex_metadata.negative.z = 0.0
m.ex_metadata.positive.elevation = 0.0
m.ex_metadata.positive.id = None
m.ex_metadata.positive.latitude = 0.0
m.ex_metadata.positive.longitude = 0.0
m.ex_metadata.positive.manufacturer = None
m.ex_metadata.positive.model = None
m.ex_metadata.positive.name = None
m.ex_metadata.positive.settings = None
m.ex_metadata.positive.type = electric
m.ex_metadata.positive.x = 0.0
m.ex_metadata.positive.x2 = 56.0
m.ex_metadata.positive.y = 0.0
m.ex_metadata.positive.y2 = 0.0
m.ex_metadata.positive.z = 0.0
m.ex_metadata.sample_rate = 0.0
m.ex_metadata.time_period.end = 1980-01-01T00:00:00+00:00
m.ex_metadata.time_period.start = 1980-01-01T00:00:00+00:00
m.ex_metadata.translated_azimuth = None
m.ex_metadata.translated_tilt = None
m.ex_metadata.type = auxiliary
m.ex_metadata.units = None
m.write_mt_file(fn_basename="test.edi")