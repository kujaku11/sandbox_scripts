# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:41:03 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mtpy import MT

# =============================================================================
edi_file = Path(r"c:\Users\jpeacock\OneDrive - DOI\mt\Mines\CO701.edi")

mt_obj = MT()
mt_obj.read(edi_file)

# =============================================================================
# survey information
# =============================================================================
mt_obj.survey_metadata.id = "Geophysics Field Camp 2023"
mt_obj.survey_metadata.project = "Mines"
mt_obj.survey_metadata.country = "USA"

# citation
mt_obj.survey_metadata.citation_dataset.authors = (
    "H. Alfaraj, S. Bin Zaqr, J. Howard, J. McCall, C. Thomas, B.S. Murphy, "
    "A.R. Miller, B. Mullett, A. Alangari, H. Alhammad, M. Alnabbat, "
    "P. Chang Huang, E. Deal, N. Dorogy, D. Lipfert, B. Passerella, B. Dugan, "
    "M.R. Siegfried, and the 2023 Mines Field Camp Session"
)
mt_obj.survey_metadata.citation_dataset.title = (
    "Mines Geophysics Field Camp 2023: Magnetotelluric Transfer Functions "
    "from North Park - Steamboat Springs, Colorado"
)
mt_obj.survey_metadata.citation_dataset.year = "2023"
mt_obj.survey_metadata.citation_dataset.doi = (
    "doi:10.17611/DP/EMTF/MINES/GFC2023"
)

# =============================================================================
# station information
# =============================================================================
mt_obj.station_metadata.id = "CO701"
mt_obj.station_metadata.geographic_name = "Walden South, CO, USA"
mt_obj.station_metadata.time_period.start = "2023-05-19T10:30:00"
mt_obj.station_metadata.time_period.end = "2023-05-25T10:30:00"
mt_obj.station_metadata.location.latitude = 40.648130
mt_obj.station_metadata.location.longitude = -106.212400
mt_obj.station_metadata.location.elevation = 2501.000
mt_obj.station_metadata.location.declination.value = 8.430
mt_obj.station_metadata.location.declination.epoch = "2020.0"

# provenance information
mt_obj.station_metadata.provenance.submitter.author = "Benjamin Murphy"
mt_obj.station_metadata.provenance.submitter.email = "bmurphy@usgs.gov"
mt_obj.station_metadata.provenance.submitter.organization = (
    "U.S. Geological Survey"
)
mt_obj.station_metadata.provenance.submitter.url = "http://geomag.usgs.gov"

mt_obj.station_metadata.provenance.creator.author = "Benjamin Murphy"
mt_obj.station_metadata.provenance.creator.email = "bmurphy@usgs.gov"
mt_obj.station_metadata.provenance.creator.organization = (
    "U.S. Geological Survey"
)
mt_obj.station_metadata.provenance.creator.url = "http://geomag.usgs.gov"


# transfer function information
mt_obj.station_metadata.transfer_function.processed_by.author = (
    "Hussain Alfaraj, Salem Bin Zaqr, Colin Thomas, Jackson Howard, "
    "James McCall, Ben"
)
mt_obj.station_metadata.transfer_function.data_quality.rating.value = 5
mt_obj.station_metadata.transfer_function.data_quality.good_from_period = 0.001
mt_obj.station_metadata.transfer_function.data_quality.good_to_period = 3000
mt_obj.station_metadata.transfer_function.data_quality.comments = (
    "Best. Data. Ever"
)
mt_obj.station_metadata.transfer_function.runs_processed = []

# =============================================================================
# Make EMTF XML
# =============================================================================
xml_obj = mt_obj.to_emtfxml()

# EMTF XML specific information
xml_obj.primary_data.filename = f"{edi_file.stem}.png"
xml_obj.attachment.filename = edi_file.name
xml_obj.attachment.description = "The original used to produce the XML"

xml_obj.copyright.acknowledgement = (
    "Data were collected during the 2023 Colorado School of Mines Geophysics "
    "Field Camp with funding from Colorado School of Mines Department of "
    "Geophysics, the Colorado School of Mines Foundation, the Society of "
    "Exploration Geophysics Foundation, and the Shell Foundation. We thank "
    "Earthscope Primary Instrument Center and Colorado Mountain College "
    "Steamboat Springs for instrument and logistics support and the "
    "Northwest District of the Colorado State Land Board for permitting data "
    "acquisition on their lands."
)
xml_obj.copyright.release_status = "Unrestricted Release"
xml_obj.copyright.conditions_of_use = (
    "All data and metadata for this survey are available free of charge and "
    "Acknowledgementsmay be copied freely, duplicated and further "
    "distributed provided that this data set is cited as the reference, and "
    "that the author(s) contributions are acknowledged as detailed in the "
    "Acknowledgements. Any papers cited in this file are only for reference. "
    "There is no requirement to cite these papers when the data are used. "
    "Whenever possible, we ask that the author(s) are notified prior to any "
    "publication that makes use of these data. While the author(s) strive to "
    "provide data and metadata of best possible quality, neither the "
    "author(s) of this data set, nor IRIS make any claims, promises, or "
    "guarantees about the accuracy, completeness, or adequacy of this "
    "information, and expressly disclaim liability for errors and omissions "
    "in the contents of this file. Guidelines about the quality or "
    "limitations of the data and metadata, as obtained from the author(s), "
    "are included for informational purposes only."
)

xml_obj.site.data_quality_notes.comments.author = "Benjamin Murphy"
xml_obj.site.data_quality_warnings.comments.author = "Benjamin Murphy"
xml_obj.site.data_quality_warnings.flag = 0

xml_obj.processing_info.sign_convention = "exp(+ i\omega t)"
xml_obj.processing_info.processing_software.last_mod = "2023-01-01"
xml_obj.processing_info.processing_software.author = "Phoenix Geophysics"


xml_obj.write(
    r"c:\Users\jpeacock\OneDrive - DOI\mt\Mines\CO701_sample.xml",
    skip_field_notes=True,
)
