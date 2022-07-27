# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 18:02:58 2021

@author: jpeacock
"""
# =============================================================================
#
# =============================================================================
from pathlib import Path
import pandas as pd
import numpy as np
from mtpy import MT

# from mt_metadata.transfer_functions.core import TF

# =============================================================================
survey_csv_fn = (
    r"c:\Users\jpeacock\OneDrive - DOI\SCEC_2019\ssaf_survey_summary.csv"
)
zmm_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\SCEC_2019\zmm_final")
zmm_list = list(zmm_path.glob("*.zmm"))

save_dir_edi = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\SCEC_2019\final_edi_new"
)
save_dir_png = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\SCEC_2019\final_png_new"
)

# =============================================================================
survey_df = pd.read_csv(survey_csv_fn)


for zmm_fn in zmm_list[22:]:
    if not zmm_fn.is_file():
        continue

    m = MT(fn=zmm_fn)
    m.save_dir = save_dir_edi

    sdf = [
        entry
        for entry in survey_df.loc[
            survey_df.station == zmm_fn.stem
        ].itertuples()
    ][0]

    # survey
    m.survey_metadata.acquired_by.author = "Jared R. Peacock"
    m.survey_metadata.acquired_by.comments = "U.S. Geological Survey"
    m.survey_metadata.citation_dataset.authors = (
        "J. R. Peacock and P.E. Share MacParland"
    )
    m.survey_metadata.citation_dataset.doi = "https://doi.org/10.5066/P990U7GE"
    m.survey_metadata.citation_dataset.year = "2022"
    m.survey_metadata.comments = None
    m.survey_metadata.country = "USA"
    m.survey_metadata.datum = "WGS84"
    m.survey_metadata.geographic_name = (
        "Southern San Andreas Fault Zone, California"
    )
    m.survey_metadata.name = "Southern San Andreas Fault Zone"
    m.survey_metadata.northwest_corner.latitude = survey_df.latitude.max()
    m.survey_metadata.northwest_corner.longitude = survey_df.longitude.min()
    m.survey_metadata.project = "Southern San Andreas Fault Zone"
    m.survey_metadata.project_lead.author = "J. R. Peacock"
    m.survey_metadata.project_lead.email = "jpeacock@usgs.gov"
    m.survey_metadata.project_lead.organization = "U. S. Geological Survey"
    m.survey_metadata.release_license = "CC0"
    m.survey_metadata.southeast_corner.latitude = survey_df.latitude.min()
    m.survey_metadata.southeast_corner.longitude = survey_df.longitude.max()
    m.survey_metadata.summary = (
        "A MT profile across Southern San Andreas Fault System near Thousand "
        "Palms Oasis funded by the Southern California Earthquake Center"
        "led by Pieter Share MacParland then at the "
        "Institute of Geoscience and Planetary Physics at the "
        "University of California San Diego (Scripps), "
        "now at Oregon State University"
    )
    m.survey_metadata.id = "SSAF2019"
    m.survey_metadata.time_period.end_date = survey_df.start.max()
    m.survey_metadata.time_period.start_date = survey_df.start.min()

    # Station
    m.station_metadata.time_period.end_date = survey_df.end.max()
    m.station_metadata.time_period.start_date = survey_df.start.min()
    m.station_metadata.acquired_by.author = (
        "U.S. Geological Survey and SCRIPPS"
    )
    m.station_metadata.acquired_by.comments = "U.S. Geological Survey"
    m.station_metadata.channel_layout = "L"
    m.station_metadata.comments = "measurement_coordinate_system = geomagnetic"
    m.station_metadata.data_type = "WBMT"
    m.station_metadata.location.declination.comments = "from https://ngdc.noaa.gov/geomag/calculators/magcalc.shtml#declination "
    m.station_metadata.location.declination.model = "WMM"
    m.station_metadata.location.declination.value = 12.41
    m.station_metadata.location.declination.epoch = "2019"
    m.station_metadata.location.elevation = sdf.elevation
    m.station_metadata.orientation.method = "compass"
    m.station_metadata.orientation.reference_frame = "geographic"
    m.station_metadata.provenance.comments = (
        "Time series archived on Science Base https://doi.org/10.5066/P990U7GE"
    )
    m.station_metadata.provenance.software.author = "Jared Peacock"
    m.station_metadata.provenance.software.name = "mt_metadata"
    m.station_metadata.provenance.software.version = "0.1.8"
    m.station_metadata.provenance.submitter.author = "Jared Peacock"
    m.station_metadata.provenance.submitter.email = "jpeacock@usgs.gov"
    m.station_metadata.provenance.submitter.organization = (
        "U.S. Geological Survey"
    )
    m.station_metadata.provenance.creator.author = "Pieter Share MacParland"
    m.station_metadata.provenance.creator.email = (
        "pieter.share@oregonstate.edu"
    )
    m.station_metadata.provenance.creator.organization = (
        "Oregon State University"
    )

    # transfer function
    m.station_metadata.transfer_function.id = zmm_fn.stem
    m.station_metadata.transfer_function.runs_processed = [f"{zmm_fn.stem}a"]
    m.station_metadata.transfer_function.processed_date = "2019-10-01"
    m.station_metadata.transfer_function.processing_parameters = []
    m.station_metadata.transfer_function.remote_references = []
    m.station_metadata.transfer_function.sign_convention = "+"
    m.station_metadata.transfer_function.units = (
        "millivolts_per_kilometer_per_nanotesla"
    )
    m.station_metadata.transfer_function.software.author = "Gary Egbert"
    m.station_metadata.transfer_function.software.name = "EMTF"
    m.station_metadata.id = zmm_fn.stem

    # run information
    m.station_metadata.runs[0].id = f"{zmm_fn.stem}a"
    m.station_metadata.runs[0].data_logger.id = sdf.data_logger

    m.station_metadata.runs[0].ex.channel_id = 4.0
    m.station_metadata.runs[0].ex.channel_number = 4
    m.station_metadata.runs[0].ex.contact_resistance.end = sdf.ex_cres_start
    m.station_metadata.runs[0].ex.contact_resistance.start = sdf.ex_cres_end
    m.station_metadata.runs[0].ex.measurement_azimuth = sdf.ex_azimuth
    m.station_metadata.runs[0].ex.dipole_length = sdf.ex_length
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

    m.station_metadata.runs[0].ey.channel_id = 5.0
    m.station_metadata.runs[0].ey.channel_number = 5
    m.station_metadata.runs[0].ey.contact_resistance.end = sdf.ey_cres_start
    m.station_metadata.runs[0].ey.contact_resistance.start = sdf.ey_cres_end
    m.station_metadata.runs[0].ey.measurement_azimuth = sdf.ey_azimuth
    m.station_metadata.runs[0].ey.dipole_length = sdf.ey_length
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

    m.station_metadata.runs[0].hx.measurement_azimuth = sdf.hx_azimuth
    m.station_metadata.runs[0].hx.measurement_tilt = 0.0
    m.station_metadata.runs[0].hx.sensor.manufacturer = "Zonge International"
    m.station_metadata.runs[0].hx.sensor.model = "ANT4"
    m.station_metadata.runs[0].hx.sensor.id = sdf.hx_sensor
    m.station_metadata.runs[0].hx.sensor.type = "magnetic induction coil"
    m.station_metadata.runs[0].hx.translated_azimuth = (
        m.station_metadata.runs[0].hx.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    m.station_metadata.runs[0].hx.translated_tilt = None
    m.station_metadata.runs[0].hx.type = "magnetic"
    m.station_metadata.runs[0].hx.units = "nanotesla"

    m.station_metadata.runs[0].hy.measurement_azimuth = sdf.hy_azimuth
    m.station_metadata.runs[0].hy.measurement_tilt = 0.0
    m.station_metadata.runs[0].hy.sensor.manufacturer = "Zonge International"
    m.station_metadata.runs[0].hy.sensor.model = "ANT4"
    m.station_metadata.runs[0].hy.sensor.id = sdf.hy_sensor
    m.station_metadata.runs[0].hy.sensor.type = "magnetic induction coil"
    m.station_metadata.runs[0].hy.translated_azimuth = (
        m.station_metadata.runs[0].hy.measurement_azimuth
        - m.station_metadata.location.declination.value
    )
    try:
        m.station_metadata.runs[0].hy.translated_tilt = None
        m.station_metadata.runs[0].hy.type = "magnetic"
        m.station_metadata.runs[0].hy.units = "nanotesla"

        m.station_metadata.runs[0].hz.measurement_azimuth = 0
        m.station_metadata.runs[0].hz.measurement_tilt = 90
        m.station_metadata.runs[
            0
        ].hz.sensor.manufacturer = "Zonge International"
        m.station_metadata.runs[0].hz.sensor.model = "ANT4"
        m.station_metadata.runs[0].hz.sensor.id = sdf.hz_sensor
        m.station_metadata.runs[0].hz.sensor.type = "magnetic induction coil"
        m.station_metadata.runs[0].hz.translated_azimuth = 0
        m.station_metadata.runs[0].hz.translated_tilt = 90
        m.station_metadata.runs[0].hz.type = "magnetic"
        m.station_metadata.runs[0].hz.units = "nanotesla"
    except AttributeError:
        print(f"{zmm_fn.stem} has no hz")

    m.write_tf_file(save_dir=save_dir_edi, file_type="edi")

    p = m.plot_mt_response(plot_num=2)
    p.save_plot(
        save_dir_png.joinpath(f"{m.station}.png").as_posix(), fig_dpi=300
    )
