# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 14:20:44 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path

# from mt_metadata import TF_XML
# from mt_metadata.transfer_functions.io.emtfxml import EMTFXML
from mt_metadata.transfer_functions.core import TF

# =============================================================================

# x0 = EMTFXML(TF_XML)
# x0.station_metadata = x0.station_metadata.copy()

edi_fn = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES\gs01.edi")

t = TF(edi_fn)
t.read()
t.survey_metadata.project = "USGS-GMEG"
t.station_metadata.fdsn.id = (
    f"{t.survey_metadata.project}.{t.station}."
    f"{t.station_metadata.time_period._start_dt.year}"
)


x = t.to_emtfxml()

# Figure file
x.primary_data.filename = f"{t.station}.png"

# Original EDI file
x.attachment.filename = edi_fn.name
x.attachment.description = "Original EDI file to make XML"

# provenance
x.provenance.creator.org_url = "https://www.usgs.gov/"
x.provenance.submitter.org_url = "https://www.usgs.gov/"

# Conditions of Use
x.copyright.conditions_of_use = (
    "All data and metadata for this survey are available free of charge and "
    "may be copied freely, duplicated and further distributed provided that "
    "this data set is cited as the reference, and that the author(s) "
    "contributions are acknowledged as detailed in the Acknowledgements. "
    "Any papers cited in this file are only for reference. There is no "
    "requirement to cite these papers when the data are used. Whenever "
    "possible, we ask that the author(s) are notified prior to any "
    "publication that makes use of these data. While the author(s) strive "
    "to provide data and metadata of best possible quality, neither the "
    "author(s) of this data set, nor IRIS make any claims, promises, or "
    "guarantees about the accuracy, completeness, or adequacy of this "
    "information, and expressly disclaim liability for errors and omissions "
    "in the contents of this file. Guidelines about the quality or "
    "limitations of the data and metadata, as obtained from the author(s), "
    "are included for informational purposes only."
)

# citation
x.copyright.citation.title = (
    "Granite Springs Play Fairway Analysis Magnetotelluric Transfer Functions"
)
x.copyright.citation.authors = "J. R. Peacock"
x.copyright.citation.year = "2017"
x.copyright.citation.survey_d_o_i = "doi:10.17611/DP/EMTF/USGS-GMEG/GS"

# site
x.site.name = "Granite Springs Valley, NV"
x.site.survey = "Granite Springs"


x.write(edi_fn.parent.joinpath(f"{edi_fn.stem}.xml"))
