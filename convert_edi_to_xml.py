# -*- coding: utf-8 -*-
"""
Created on Mon Jan 09 16:20:27 2017

@author: jpeacock
"""
import os
import mtpy.core.mt as mt
import xml.etree.ElementTree as ET
import datetime
from xml.dom import minidom

dt_fmt = "%Y-%m-%dT%H:%M:%S"

edi_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\EDI_Files_birrp_mshs\Rotated_m18_deg\ms11.edi"

mt_obj = mt.MT(edi_fn)

emtf = ET.Element("EM_TF")

description = ET.SubElement(emtf, "Description")
description.text = "Magnetotelluric Transfer Functions"

product_id = ET.SubElement(emtf, "ProductID")
product_id.text = mt_obj.station

sub_type = ET.SubElement(emtf, "SubType")
sub_type.text = r"MT_TF"

notes = ET.SubElement(emtf, "Notes")
notes.text = "Notes on data type"

tags = ET.SubElement(emtf, "Tags")
tags.text = "impedance,tipper"

external_url = ET.SubElement(emtf, "ExternalURL")
external_url.text = r"http://www.iris.edu/mda/EM/{0}".format(mt_obj.station)

attachment = ET.SubElement(emtf, "Attachment")
attachment_fn = ET.SubElement(attachment, "Filename")
attachment_fn.text = os.path.basename(edi_fn)
attachment_description = ET.SubElement(attachment, "Description")
attachment_description.text = r"Original .EDI file used to produce XML"

provenance = ET.SubElement(emtf, "Provenance")
prov_create_time = ET.SubElement(provenance, "CreateTime")
prov_create_time.text = datetime.datetime.strftime(datetime.datetime.utcnow(), dt_fmt)
prov_creating_application = ET.SubElement(provenance, "CreatingApplication")
prov_creating_application.text = r"MTpy"

prov_creator = ET.SubElement(provenance, "Creator")
prov_creator_name = ET.SubElement(prov_creator, "Name")
prov_creator_name.text = r"Jared Peacock"
prov_creator_email = ET.SubElement(prov_creator, "Email")
prov_creator_email.text = r"jpeacock@usgs.gov"
prov_creator_org = ET.SubElement(prov_creator, "Org")
prov_creator_org.text = r"U.S. Geological Survey"
prov_creator_url = ET.SubElement(prov_creator, "OrgURL")
prov_creator_url.text = r"www.usgs.gov"

prov_submitter = ET.SubElement(provenance, "Submitter")
prov_submitter_name = ET.SubElement(prov_submitter, "Name")
prov_submitter_name.text = r"Jared Peacock"
prov_submitter_email = ET.SubElement(prov_submitter, "Email")
prov_submitter_email.text = r"jpeacock@usgs.gov"
prov_submitter_org = ET.SubElement(prov_submitter, "Org")
prov_submitter_org.text = r"U.S. Geological Survey"
prov_submitter_url = ET.SubElement(prov_submitter, "OrgURL")
prov_submitter_url.text = r"www.usgs.gov"

copy_right = ET.SubElement(emtf, "Copyright")
copy_right_citation = ET.SubElement(copy_right, "Citation")
copy_right_citation_title = ET.SubElement(copy_right_citation, "Title")
copy_right_citation_title.text = r"Imaging the magmatic system of Mono Basin, California, with magnetotellurics in three dimensions"
copy_right_citation_authors = ET.SubElement(copy_right_citation, "Authors")
copy_right_citation_authors.text = (
    r"Jared R. Peacock, Maggie T. Mangan, Darcy K. McPhee, David A. Ponce"
)
copy_right_citation_year = ET.SubElement(copy_right_citation, "Year")
copy_right_citation_year.text = r"2015"
copy_right_citation_journal = ET.SubElement(copy_right_citation, "Journal")
copy_right_citation_journal.text = r"Journal of Geophysical Research: Solid Earth"
copy_right_citation_vol = ET.SubElement(copy_right_citation, "Volume")
copy_right_citation_vol.text = r"120"
copy_right_citation_doi = ET.SubElement(copy_right_citation, "DOI")
copy_right_citation_doi.text = r"10.1002/2015JB012071"
copy_right_release = ET.SubElement(copy_right, "ReleaseStatus")
copy_right_release.text = r"Public Domain"
copy_right_conditions = ET.SubElement(copy_right, "ConditionsOfUse")
copy_right_conditions.text = r"All data and metadata for this survey are available free of charge and may be copied freely, duplicated and further distributed provided this data set is cited as the reference. While the author(s) strive to provide data and metadata of best possible quality, neither the author(s) of this data set, not IRIS make any claims, promises, or guarantees about the accuracy, completeness, or adequacy of this information, and expressly disclaim liability for errors and omissions in the contents of this file. Guidelines about the quality or limitations of the data and metadata, as obtained from the author(s), are included for informational purposes only."

site = ET.SubElement(emtf, "Site")
site_project = ET.SubElement(site, "Project")
site_project.text = r"California Volcano Hazards"
site_survey = ET.SubElement(site, "Survey")
site_survey.text = r"Mono Basin, CA"
site_year_collected = ET.SubElement(site, "YearCollected")
site_year_collected.text = r"2014"
site_id = ET.SubElement(site, "Id")
site_id.text = mt_obj.station
site_name = ET.SubElement(site, "Name")
site_name.text = r"Mono Basin, CA"
site_location = ET.SubElement(site, "Location", {"datum": "WGS84"})
site_location_lat = ET.SubElement(site_location, "Latitude")
site_location_lat.text = "{0:.5f}".format(mt_obj.lat)
site_location_lon = ET.SubElement(site_location, "Longitude")
site_location_lon.text = "{0:.5f}".format(mt_obj.lon)
site_location_elev = ET.SubElement(site_location, "Elevation", {"units": "meters"})
site_location_elev.text = "{0:.3f}".format(mt_obj.elev)
site_location_dec = ET.SubElement(site_location, "Declination", {"epoch": "2015"})
site_location_dec.text = r"12.8"
site_aqcby = ET.SubElement(site, "AcquiredBy")
site_aqcby.text = mt_obj.edi_object.Header.acqby.upper()
site_start = ET.SubElement(site, "Start")
site_start.text = mt_obj.edi_object.Header.acqdate.replace(r"/", "-") + "T00:00:00"
site_end = ET.SubElement(site, "End")
site_end.text = mt_obj.edi_object.Header.acqdate.replace(r"/", "-") + "T00:00:00"
site_run = ET.SubElement(site, "RunList")
site_run.text = mt_obj.station

site_data_qc = ET.SubElement(site, "DataQualityNotes")
site_data_qc_rating = ET.SubElement(site_data_qc, "Rating")
site_data_qc_rating.text = r"5"
site_data_qc_comments = ET.SubElement(
    site_data_qc, "Comments", {"author": "Jared Peacock"}
)
site_data_qc_comments.text = "Good"

processing = ET.SubElement(emtf, "ProcessingInfo")


# make a nice print out
reparsed = minidom.parseString(ET.tostring(emtf, "utf-8"))
print(reparsed.toprettyxml(indent="    "))
