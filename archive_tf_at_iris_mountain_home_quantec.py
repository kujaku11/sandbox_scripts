# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 10:31:05 2022

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path

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
survey = "PFA_MountainHome"
year = "2016"
declination = 13.04
plot = True

project = f"{organization}-{science_center}"

# path to TF files
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\MountainHome\EDI_Files_Archive\quantec"
)

# save files to one directory
save_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\transfer_function_archive"
).joinpath(survey)

save_path.mkdir(exist_ok=True)


### run this to loop over all edi files in folder
# for edi_file in edi_path.glob("*.edi"):

### use this to just do one file to make sure everything looks good
# for edi_file in list(edi_path.glob("*.edi"))[0:1]:
for edi_file in edi_path.glob("*.edi"):
    mt_obj = MT()
    mt_obj.read(edi_file)
    fn_name = f"{project}.{year}.{mt_obj.station}"

    # remove unnecessary runs
    remove_runs = []
    for run_id in mt_obj.station_metadata.runs.keys():
        if mt_obj.station not in run_id:
            remove_runs.append(run_id)

    for remove_run in remove_runs:
        mt_obj.station_metadata.runs.remove(remove_run)

    # # get row from survey data frame
    # row = survey_summary[survey_summary.station == mt_obj.station.lower()]
    # row = row.iloc[0]

    # update some of the metadata
    mt_obj.survey_metadata.id = survey
    mt_obj.survey_metadata.funding_source.organization = [
        "U.S. Department of Energy Geothermal Technologies Office"
    ]
    mt_obj.survey_metadata.funding_source.grant_id = ["DE-AC02-05CH11231"]
    mt_obj.survey_metadata.funding_source.comments = (
        "This work was also supported with funding by the Assistant Secretary"
        " for Energy Efficiency and Renewable Energy, Geothermal Technologies "
        "Office, of the U.S. Department under the U.S. Department of Energy "
        "Contract No. DE-AC02-05CH11231 with Lawrence Berkeley National "
        "Laboratory."
    )

    # citation
    mt_obj.survey_metadata.citation_dataset.authors = (
        "Quantec Geoscience, E. Gasperikova"
    )
    mt_obj.survey_metadata.citation_dataset.title = (
        "Magnetotelluric data near Mountain Home, Idaho"
    )
    mt_obj.survey_metadata.citation_dataset.doi = (
        f"doi:10.17611/DP/EMTF/{science_center}/{survey}"
    )
    mt_obj.survey_metadata.citation_dataset.year = year

    # project
    mt_obj.survey_metadata.project = project
    mt_obj.survey_metadata.country = "USA"

    mt_obj.station_metadata.location.declination.value = declination
    mt_obj.station_metadata.location.declination.model = "WMM"
    mt_obj.station_metadata.location.declination.epoch = "2020"
    mt_obj.station_metadata.geographic_name = "Mountain Home, ID, USA"
    mt_obj.station_metadata.acquired_by.name = "Quantec Geoscience"
    mt_obj.station_metadata.orientation.method = "compass"
    mt_obj.station_metadata.orientation.reference_frame = "geographic"

    # provenance: creator
    mt_obj.station_metadata.provenance.archive.name = fn_name
    mt_obj.station_metadata.provenance.software.name = "mt-metadata"
    mt_obj.station_metadata.provenance.software.version = mt_metadata_version

    mt_obj.station_metadata.provenance.create_time = str(MTime().now()).split(
        "."
    )[0]
    mt_obj.station_metadata.provenance.creator.name = "Quantec Geoscience"
    mt_obj.station_metadata.provenance.creator.email = (
        r"https://quantecgeo.com/contact-us/"
    )
    mt_obj.station_metadata.provenance.creator.organization = (
        "Quantec Geoscience"
    )
    mt_obj.station_metadata.provenance.creator.url = r"https://quantecgeo.com"

    # provenance: submitter
    mt_obj.station_metadata.provenance.submitter.name = "Jared Peacock"
    mt_obj.station_metadata.provenance.submitter.email = "jpeacock@usgs.gov"
    mt_obj.station_metadata.provenance.submitter.organization = (
        "U.S. Geological Survey"
    )
    mt_obj.station_metadata.provenance.submitter.url = r"https:\\www.usgs.gov"

    # transfer function
    mt_obj.station_metadata.transfer_function.runs_processed = [
        f"{mt_obj.station}a"
    ]
    mt_obj.station_metadata.transfer_function.processing_type = (
        "Robust Remote Reference Processing"
    )
    mt_obj.station_metadata.transfer_function.data_quality.rating.value = int(
        mt_obj.estimate_tf_quality(round_qf=True)
    )
    mt_obj.station_metadata.comments = ""

    mt_obj.station_metadata.transfer_function.sign_convention = (
        "exp(+ i\omega t)"
    )
    mt_obj.station_metadata.transfer_function.software.author = (
        "Quantec Geoscience"
    )
    mt_obj.station_metadata.transfer_function.software.name = "MTeditor_v1d"
    mt_obj.station_metadata.transfer_function.software.version = "1d"
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
    xml_obj.copyright.citation.year = year
    xml_obj.copyright.citation.survey_d_o_i = (
        f"doi:10.17611/DP/EMTF/{science_center}/{survey}"
    )
    # xml_obj.copyright.citation.selected_publications = "GRC paper"
    xml_obj.copyright.acknowledgement = (
        "This work was also supported with funding by the Assistant Secretary"
        " for Energy Efficiency and Renewable Energy, Geothermal Technologies "
        "Office, of the U.S. Department under the U.S. Department of Energy "
        "Contract No. DE-AC02-05CH11231 with Lawrence Berkeley National "
        "Laboratory.  Lawerence Berekeley National Lab contracted Quantec "
        "Geoscience to collect and process the magnetotelluric data."
    )
    xml_obj.copyright.additional_info = (
        "These data were collected as part of a Play Fairway project to "
        "develop a 3D electrical resistivity model to characterize blind "
        "geothermal resources in the region of Mountain Home, ID."
    )

    xml_obj.site.survey = survey

    xml_obj.site.data_quality_notes.good_from_period = 0.004
    xml_obj.site.data_quality_notes.good_to_period = 1200
    xml_obj.site.data_quality_notes.comments.author = ""
    xml_obj.site.data_quality_notes.comments.value = ""

    xml_obj.site.data_quality_warnings.comments.author = "Jared Peacock"
    xml_obj.site.data_quality_warnings.comments.value = (
        "Check transfer function before using"
    )

    # processing
    xml_obj.processing_info.processing_software.name = "MTEdidtor_v1d"
    xml_obj.processing_info.processing_software.last_mod = "2016-01-01"
    xml_obj.processing_info.processing_tag = xml_obj.site.id

    # write to file
    xml_obj.write(
        save_path.joinpath(f"{fn_name}.xml"),
        skip_field_notes=True,
    )

    # create plot
    if plot:
        p = mt_obj.plot_mt_response(plot_num=2)
        p.save_plot(save_path.joinpath(f"{fn_name}.png"), fig_dpi=300)

    # rewrite edi file
    edi_obj = mt_obj.write(save_path.joinpath(f"{fn_name}.edi"))
