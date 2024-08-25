# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 10:31:05 2022

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import pandas as pd

from mtpy import MT

from mt_metadata.utils.mttime import MTime
from mt_metadata import __version__ as mt_metadata_version

# =============================================================================
### EMFTXML's convention for naming things
### project = "USGS-GMEG"
### survey = "geographic name"

### doi = "10.17611/DP/EMTF/science_center/survey_name"
### product_id = "project-survey-year"
organization = "USGS"
science_center = "GMEG"
survey = "GabbsValley"
year = "2017"
declination = 12.9
plot = True

project = f"{organization}-{science_center}"

# path to TF files
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\EDI_Files\PFA"
)

# save files to one directory
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\transfer_function_archive"
).joinpath(survey)

save_path.mkdir(exist_ok=True)

# survey information
survey_summary = pd.read_csv(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\GabbsValley\survey_summary.csv"
)
survey_summary.start = pd.to_datetime(survey_summary.start)
survey_summary.end = pd.to_datetime(survey_summary.end)
survey_summary["start_date"] = [s.date() for s in survey_summary.start]

### run this to loop over all edi files in folder
# for edi_file in edi_path.glob("*.edi"):

### use this to just do one file to make sure everything looks good
# for edi_file in list(edi_path.glob("*.edi"))[0:1]:
for edi_file in edi_path.glob("*.edi"):
    mt_obj = MT()
    mt_obj.read(edi_file)
    fn_name = f"{project}.{year}.{mt_obj.station.lower()}"

    # remove unnecessary runs
    remove_runs = []
    for run_id in mt_obj.station_metadata.runs.keys():
        if mt_obj.station not in run_id:
            remove_runs.append(run_id)

    for remove_run in remove_runs:
        mt_obj.station_metadata.runs.remove(remove_run)

    mt_obj.station_metadata.runs[0].id = mt_obj.station_metadata.runs[
        0
    ].id.lower()

    mt_obj.station = mt_obj.station.lower()
    mt_obj.tf_id = mt_obj.station.lower()

    # get row from survey data frame
    row = survey_summary[survey_summary.station == mt_obj.station]
    row = row.iloc[0]

    # update some of the metadata
    mt_obj.survey_metadata.id = survey
    mt_obj.survey_metadata.funding_source.organization = [
        "Department of Energy",
        "U.S. Geological Survey Geothermal Resources Investigation Project",
    ]
    mt_obj.survey_metadata.funding_source.grant_id = ["DE-EE0006731"]
    mt_obj.survey_metadata.funding_source.comments = (
        "This project was funded by the Department "
        "of Energy, Office of Energy Efficiency and Renewable Energy (EERE), "
        "Geothermal Technologies Offices, under Award Number DE-EE0006731 "
        "granted to the University of Nevada Reno, and by the Geothermal "
        "Resources Investigation Project (GRIP) funded by the Energy "
        "Resources Program of U.S. Geological Survey. "
    )

    # release license
    mt_obj.survey_metadata.release_license = "CC-BY-4.0"

    # citation
    mt_obj.survey_metadata.citation_dataset.authors = "J. R. Peacock "
    mt_obj.survey_metadata.citation_dataset.title = (
        "Magnetotelluric data in the southern Gabbs Valley region, Nevada for "
        "Play Fairway Analysis of blind geothermal systems"
    )
    mt_obj.survey_metadata.citation_dataset.doi = (
        f"doi:10.17611/DP/EMTF/{science_center}/{survey}"
    )
    mt_obj.survey_metadata.citation_dataset.year = year

    # Journal Article
    mt_obj.survey_metadata.citation_journal.title = (
        "Discovery and analysis of a blind geothermal system in southeastern "
        "Gabbs Valley, western Nevada, USA"
    )
    mt_obj.survey_metadata.citation_journal.authors = (
        "Craig, J. W., Faulds, J. E., Hinz, N. H., Earney, T. E., "
        "Schermerhorn, W. D., Siler, D. L., Glen, J. M., Peacock, J. R., "
        "Coolbaugh, M. F., Deoreo, S. B."
    )
    mt_obj.survey_metadata.citation_journal.doi = (
        "https://doi.org/10.1016/j.geothermics.2021.102177"
    )
    mt_obj.survey_metadata.citation_journal.journal = "Geothermics"
    mt_obj.survey_metadata.citation_journal.year = 2021
    mt_obj.survey_metadata.citation_journal.volume = 97

    # project
    mt_obj.survey_metadata.project = project
    mt_obj.survey_metadata.country = "USA"

    # site information
    mt_obj.station_metadata.runs[0].time_period.start = row.start
    mt_obj.station_metadata.runs[0].time_period.end = row.end
    mt_obj.station_metadata.update_time_period()
    mt_obj.survey_metadata.update_time_period()

    mt_obj.station_metadata.location.declination.value = declination
    mt_obj.station_metadata.location.declination.model = "WMM"
    mt_obj.station_metadata.location.declination.epoch = year
    mt_obj.station_metadata.geographic_name = "Southern Gabbs Valley, NV, USA"
    mt_obj.survey_metadata.geographic_name = "Southern Gabbs Valley, NV, USA"
    mt_obj.station_metadata.acquired_by.name = "U.S. Geological Survey"
    mt_obj.station_metadata.orientation.method = "compass"
    mt_obj.station_metadata.orientation.reference_frame = "geographic"

    # run in formation
    mt_obj.station_metadata.runs[0].data_logger.id = row.instrument_id
    mt_obj.station_metadata.runs[0].data_logger.manufacturer = (
        "Zonge International"
    )
    mt_obj.station_metadata.runs[0].data_logger.type = "ZEN 32-bit"
    mt_obj.station_metadata.runs[0].data_logger.name = "ZEN"

    ### ex
    mt_obj.station_metadata.runs[0].ex.dipole_length = row.dipole_ex
    mt_obj.station_metadata.runs[0].ex.positive.x2 = row.dipole_ex
    mt_obj.station_metadata.runs[0].ex.positive.y2 = 0
    mt_obj.station_metadata.runs[0].ex.translated_azimuth = 0
    mt_obj.station_metadata.runs[0].ex.channel_number = 4
    mt_obj.station_metadata.runs[0].ex.positive.manufacturer = "Borin"
    mt_obj.station_metadata.runs[0].ex.positive.type = "Ag-AgCl"
    mt_obj.station_metadata.runs[0].ex.positive.name = "Stelth 1"
    mt_obj.station_metadata.runs[0].ex.negative.manufacturer = "Borin"
    mt_obj.station_metadata.runs[0].ex.negative.type = "Ag-AgCl"
    mt_obj.station_metadata.runs[0].ex.negative.name = "Stelth 1"

    ### ey
    mt_obj.station_metadata.runs[0].ey.dipole_length = row.dipole_ey
    mt_obj.station_metadata.runs[0].ey.positive.x2 = 0
    mt_obj.station_metadata.runs[0].ey.positive.y2 = row.dipole_ey
    mt_obj.station_metadata.runs[0].ey.measurement_azimuth = 90
    mt_obj.station_metadata.runs[0].ey.translated_azimuth = 90
    mt_obj.station_metadata.runs[0].ey.channel_number = 5
    mt_obj.station_metadata.runs[0].ey.positive.manufacturer = "Borin"
    mt_obj.station_metadata.runs[0].ey.positive.type = "Ag-AgCl"
    mt_obj.station_metadata.runs[0].ey.positive.name = "Stelth 1"
    mt_obj.station_metadata.runs[0].ey.negative.manufacturer = "Borin"
    mt_obj.station_metadata.runs[0].ey.negative.type = "Ag-AgCl"
    mt_obj.station_metadata.runs[0].ey.negative.name = "Stelth 1"

    ### hx
    mt_obj.station_metadata.runs[0].hx.sensor.id = int(row.hx)
    mt_obj.station_metadata.runs[0].hx.sensor.manufacturer = (
        "Zonge International"
    )
    mt_obj.station_metadata.runs[0].hx.sensor.type = "Induction Coil"
    mt_obj.station_metadata.runs[0].hx.sensor.model = "ANT-4"
    mt_obj.station_metadata.runs[0].hx.channel_id = int(row.hx)
    mt_obj.station_metadata.runs[0].hx.translated_azimuth = 0
    mt_obj.station_metadata.runs[0].hx.channel_number = 1

    ### hy
    mt_obj.station_metadata.runs[0].hy.sensor.id = int(row.hy)
    mt_obj.station_metadata.runs[0].hy.sensor.manufacturer = (
        "Zonge International"
    )
    mt_obj.station_metadata.runs[0].hy.sensor.type = "Induction Coil"
    mt_obj.station_metadata.runs[0].hy.sensor.model = "ANT-4"
    mt_obj.station_metadata.runs[0].hy.channel_id = int(row.hy)
    mt_obj.station_metadata.runs[0].hy.measurement_azimuth = 90
    mt_obj.station_metadata.runs[0].hy.translated_azimuth = 90
    mt_obj.station_metadata.runs[0].hy.channel_number = 2

    ### hz
    if mt_obj.has_tipper():
        mt_obj.station_metadata.runs[0].hz.sensor.id = int(row.hz)
        mt_obj.station_metadata.runs[0].hz.sensor.manufacturer = (
            "Zonge International"
        )
        mt_obj.station_metadata.runs[0].hz.sensor.type = "Induction Coil"
        mt_obj.station_metadata.runs[0].hz.sensor.model = "ANT-4"
        mt_obj.station_metadata.runs[0].hz.channel_id = int(row.hz)
        mt_obj.station_metadata.runs[0].hz.channel_number = 3
        mt_obj.station_metadata.runs[0].hz.measurement_tilt = 90

    # provenance: creator
    mt_obj.station_metadata.provenance.archive.name = fn_name
    mt_obj.station_metadata.provenance.software.name = "mt-metadata"
    mt_obj.station_metadata.provenance.software.version = mt_metadata_version

    mt_obj.station_metadata.provenance.create_time = str(MTime().now()).split(
        "."
    )[0]
    mt_obj.station_metadata.provenance.creator.name = "Jared Peacock"
    mt_obj.station_metadata.provenance.creator.email = "jpeacock@usgs.gov"
    mt_obj.station_metadata.provenance.creator.organization = (
        "U.S. Geological Survey"
    )
    mt_obj.station_metadata.provenance.creator.url = r"https://www.usgs.gov"

    # provenance: submitter
    mt_obj.station_metadata.provenance.submitter.name = "Jared Peacock"
    mt_obj.station_metadata.provenance.submitter.email = "jpeacock@usgs.gov"
    mt_obj.station_metadata.provenance.submitter.organization = (
        "U.S. Geological Survey"
    )
    mt_obj.station_metadata.provenance.submitter.url = r"https://www.usgs.gov"

    # transfer function
    rr = survey_summary.loc[
        survey_summary.start_date == row.start.date(), ["station"]
    ].station.to_list()
    rr.remove(mt_obj.station)
    mt_obj.station_metadata.transfer_function.remote_references = rr

    processing_parameters = [
        c.split(".", 2)[-1].replace(" = ", "=")
        for c in mt_obj.station_metadata.comments.split("\n")
        if "processing_parameters" in c
        and "nread" not in c
        and "nskip" not in c
        and "filnam" not in c
    ]
    mt_obj.station_metadata.transfer_function.processing_parameters = (
        processing_parameters
    )
    mt_obj.station_metadata.transfer_function.runs_processed = [
        f"{mt_obj.station}a"
    ]
    mt_obj.station_metadata.transfer_function.processing_type = (
        "Bounded Influence Robust Remote Reference Processing"
    )
    mt_obj.station_metadata.transfer_function.data_quality.rating.value = int(
        mt_obj.estimate_tf_quality(round_qf=True)
    )
    mt_obj.station_metadata.comments = ""

    mt_obj.station_metadata.transfer_function.sign_convention = (
        "exp(+ i\omega t)"
    )
    mt_obj.station_metadata.transfer_function.software.author = "A. Chave"
    mt_obj.station_metadata.transfer_function.software.name = "BIRRP"
    mt_obj.station_metadata.transfer_function.software.version = "5.1.1"
    mt_obj.station_metadata.transfer_function.units = "[mV/km]/[nT]"

    # might be easiest to directly adjust the xml unles you want to rewrite the
    # EDI with updated metadata
    xml_obj = mt_obj.to_emtfxml()

    # update metadata
    xml_obj.product_id = fn_name
    xml_obj.primary_data.filename = f"{fn_name}.png"

    # attachment: original TF file
    xml_obj.attachment.filename = f"{fn_name}.edi"
    xml_obj.attachment.description = "Original transfer function file used"

    # provenance: creator
    xml_obj.provenance.create_time = str(MTime().now()).split(".")[0]

    # copyright: citation
    xml_obj.copyright.release_status = "Data Citation Required"
    xml_obj.copyright.acknowledgement = ", ".join(
        mt_obj.survey_metadata.funding_source.organization
    )
    xml_obj.copyright.additional_info = (
        mt_obj.survey_metadata.funding_source.comments
    )

    # Journal Publication
    xml_obj.copyright.selected_publications = (
        f"{mt_obj.survey_metadata.citation_journal.authors}, "
        f"({mt_obj.survey_metadata.citation_journal.year}), "
        f"{mt_obj.survey_metadata.citation_journal.title}, "
        f"{mt_obj.survey_metadata.citation_journal.journal}, "
        f"{mt_obj.survey_metadata.citation_journal.volume}, "
        f"{mt_obj.survey_metadata.citation_journal.doi}."
    )

    xml_obj.site.data_quality_notes.good_from_period = 0.0013
    xml_obj.site.data_quality_notes.good_to_period = 2048
    xml_obj.site.data_quality_notes.comments.author = "Jared Peacock"
    xml_obj.site.data_quality_notes.comments.value = "Minimal noise sources"

    xml_obj.site.data_quality_warnings.comments.author = "Jared Peacock"
    xml_obj.site.data_quality_warnings.comments.value = (
        "Check transfer function before using"
    )

    # processing
    xml_obj.processing_info.processing_software.name = (
        mt_obj.station_metadata.transfer_function.software.name
    )
    xml_obj.processing_info.processing_software.last_mod = "2015-05-01"
    xml_obj.processing_info.processing_tag = xml_obj.site.id

    # run information
    xml_obj.field_notes.run_list[0].sampling_rate = 256
    xml_obj.field_notes.run_list[0].comments.author = "J. Peacock"
    xml_obj.field_notes.run_list[0].comments.value = (
        "Data were collected on a repeating schedule of 10 minutes at 4096 "
        "samples/second, then 7 hours and 50 minutes at 256 samples/second. "
        "All stations synchronously collect on the same schedule."
    )

    # write to file
    xml_obj.write(
        save_path.joinpath(f"{fn_name}.xml"),
        skip_field_notes=False,
    )

    # create plot
    if plot:
        p = mt_obj.plot_mt_response(plot_num=2)
        p.save_plot(save_path.joinpath(f"{fn_name}.png"), fig_dpi=300)

    # rewrite edi file
    edi_obj = mt_obj.write(save_path.joinpath(f"{fn_name}.edi"))
