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

# =============================================================================
### EMFTXML's convention for naming things
### project = "USGS-GMEG"
### survey = "geographic name"

### doi = "10.17611/DP/EMTF"
### product_id = "project-survey-year"

project = "USGS-GMEG"
survey = "INGENIOUS_ArgentaRise"
year = "2022"

# path to TF files
edi_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Battle_Mountain\EDI_files_birrp\edited\GeographicNorth"
)


### run this to loop over all edi files in folder
# for edi_file in edi_path.glob("*.edi"):

### use this to just do one file to make sure everything looks good
for edi_file in list(edi_path.glob("*.edi"))[0:1]:
    mt_obj = MT()
    mt_obj.read(edi_file)

    # might be easiest to directly adjust the xml unles you want to rewrite the
    # EDI with updated metadata
    xml_obj = mt_obj.to_emtfxml()

    # update metadata
    xml_obj.product_id = f"{project}_{survey}.{mt_obj.station}.{year}"
    xml_obj.primary_data.filename = f"{survey}_{mt_obj.station}.png"

    # attachment: original TF file
    xml_obj.attachment.filename = edi_file.name
    xml_obj.attachment.description = "Original transfer function file used"

    # provenance: creator
    xml_obj.provenance.creating_application = "mtpy-v2 (v2.0.7)"
    xml_obj.provenance.create_time = str(MTime().now()).split(".")[0]
    xml_obj.provenance.creator.name = "Jared Peacock"
    xml_obj.provenance.creator.email = "jpeacock@usgs.gov"
    xml_obj.provenance.creator.org = "U.S. Geological Survey"
    xml_obj.provenance.creator.org_url = "https:\\www.usgs.gov"

    # provenance: submitter (I think is always Anna)
    xml_obj.provenance.submitter.name = "Anna Kelbert"
    xml_obj.provenance.submitter.email = "akelbert@usgs.gov"
    xml_obj.provenance.submitter.org = "U.S. Geological Survey"
    xml_obj.provenance.submitter.org_url = "https:\\www.usgs.gov"

    # copyright: citation
    xml_obj.copyright.citation.selected_publications = "GRC paper"
    xml_obj.copyright.acknowledgement = "INGENIOUS DOE project #"
    xml_obj.copyright.additional_info = (
        "These data were collected as part of the INGENIOUS project to "
        "develop a 3D electrical resistivity model to characterize geothermal "
        "resources."
    )

    # site:
    xml_obj.site.project = project
    xml_obj.site.survey = survey
    xml_obj.site.year_collected = year
    xml_obj.site.country = "USA"
    xml_obj.site.name = "Argenta Rise, NV, USA"
    xml_obj.site.location.declination.value = 12.6
    xml_obj.site.location.declination.model = "IGRF"
    xml_obj.site.acquired_by = "U.S Geological Survey"

    xml_obj.site.data_quality_notes.rating = 5
    xml_obj.site.data_quality_notes.good_from_period = 0.003
    xml_obj.site.data_quality_notes.good_to_period = 2048
    xml_obj.site.data_quality_notes.comments.author = "Jared Peacock"
    xml_obj.site.data_quality_notes.comments.value = "Power lines"

    # write to file
    xml_obj.write(
        edi_file.parent.joinpath(
            f"{project}.{year}.{mt_obj.station}.xml", skip_field_notes=True
        )
    )
