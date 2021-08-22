# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 14:11:43 2018

@author: jpeacock
"""

import xml.etree.cElementTree as ET
import xml.dom.minidom as minidom
import datetime

# =============================================================================
# Input data
# =============================================================================
class Person(object):
    """
    Data type for the submitter
    """

    def __init__(self):
        self.name = None
        self.org = None
        self.address = None
        self.city = None
        self.state = None
        self.postal = None
        self.phone = None
        self.email = None
        self.country = None
        self.position = None
        self.science_center = None
        self.program = None
        self.liability = None
        self.funding_source = None


class Citation(object):
    """
    Data type for a citation
    """

    def __init__(self):
        self.author = None
        self.title = None
        self.journal = None
        self.date = None
        self.issue = None
        self.volume = None
        self.doi_url = None


class Survey(object):
    """
    data type to hold survey information
    """

    def __init__(self):
        self.begin_date = None
        self.end_date = None
        self.east = None
        self.west = None
        self.north = None
        self.south = None
        self.elev_min = None
        self.elev_max = None


class Processing(object):
    """
    Data type for processing steps
    """

    def __init__(self):
        self.step_01 = None
        self.date_01 = None


class Attachment(object):
    """
    Data type for attachments
    """

    def __int__(self):
        self.fn = None
        self.description = None


class SurveyMetadata(object):
    """
    Container for important information to put in the metadata xml file
    """

    def __init__(self, **kwargs):

        self.usgs_str = "U.S. Geological Survey"
        self.authors = None
        self.title = None
        self.doi_url = None
        self.journal_citation = Citation()
        self.purpose = None
        self.abstract = None
        self.supplement_info = None
        self.survey = Survey()
        self.submitter = Person()

        self.sc_dict = {
            "GGGSC": "Geology, Geophysics, and Geochemistry Science Center",
            "GMEGSC": "Geology, Minerals, Energy, and Geophysics Science Center",
        }
        self.program_dict = {
            "MRP": "Mineral Resources Program",
            "VHP": "Volcano Hazards Program",
        }

        self.keywords_general = None
        self.keywords_thesaurus = None
        self.locations = None

        self.use_constraint = None
        self.science_base = Person()
        self.complete_warning = None
        self.horizontal_accuracy = None
        self.vertical_accuracy = None
        self.processing = Processing()
        self.guide = Attachment()
        self.dictionary = Attachment()
        self.shapefile = Attachment()

        self.metadata = ET.Element("metadata")

        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

    def read_config_file(self, config_fn):
        """
        Read in configuration file
        """

        with open(config_fn, "r") as fid:
            lines = fid.readlines()

        for line in lines:
            if line.find("#") == 0 or len(line) < 2:
                continue
            key, value = [item.strip() for item in line.strip().split("=")]
            if key.find("."):
                obj, obj_attr = key.split(".")
                setattr(getattr(self, obj), obj_attr, value)
            else:
                setattr(self, key, value)


## =============================================================================
## main element
## =============================================================================
# metadata = ET.Element('metadata')
#
## =============================================================================
## ID information
## =============================================================================
# idinfo = ET.SubElement(metadata, 'idinfo')
#
# citation = ET.SubElement(idinfo, 'citation')
# citeinfo = ET.SubElement(citation, 'citeinfo')
# for author in authors:
#    ET.SubElement(citeinfo, 'origin').text = author
# ET.SubElement(citeinfo, 'pubdate').text = year
# ET.SubElement(citeinfo, 'title').text = title
# ET.SubElement(citeinfo, 'geoform').text = 'ASCII, shapefile, image'
#
# pubinfo = ET.SubElement(citeinfo, 'pubinfo')
# ET.SubElement(pubinfo, 'pubplace').text = 'Menlo Park, CA'
# ET.SubElement(pubinfo, 'publish').text = usgs_str
#
# ET.SubElement(citeinfo, 'onlink').text = doi_url
## journal publication
# if journal_citation:
#    journal = ET.SubElement(citeinfo, 'lworkcit')
#    jciteinfo = ET.SubElement(journal, 'citeinfo')
#    for author in journal_citation['author']:
#        ET.SubElement(jciteinfo, 'origin').text = author
#    ET.SubElement(jciteinfo, 'pubdate').text = journal_citation['date']
#    ET.SubElement(jciteinfo, 'title').text = journal_citation['title']
#    ET.SubElement(jciteinfo, 'geoform').text = 'Publication'
#    serinfo = ET.SubElement(jciteinfo, 'serinfo')
#    ET.SubElement(serinfo, 'sername').text = journal_citation['journal']
#    ET.SubElement(serinfo, 'issue').text = journal_citation['volume']
#
#    jpubinfo = ET.SubElement(jciteinfo, 'pubinfo')
#    ET.SubElement(jpubinfo, 'pubplace').text = 'Menlo Park, CA'
#    ET.SubElement(jpubinfo, 'publish').text = usgs_str
#
#    ET.SubElement(jciteinfo, 'onlink').text = journal_citation['doi_url']
#
## description
# description = ET.SubElement(idinfo, 'descript')
# ET.SubElement(description, 'abstract').text = abstract
# ET.SubElement(description, 'purpose').text = purpose
# ET.SubElement(description, 'supplinf').text = supplement_info
#
## dates covered
# time_period = ET.SubElement(idinfo, 'timeperd')
# time_info = ET.SubElement(time_period, 'timeinfo')
# dates = ET.SubElement(time_info, 'rngdates')
# ET.SubElement(dates, 'begdate').text = survey_begin
# ET.SubElement(dates, 'enddate').text = survey_end
# ET.SubElement(time_info, 'current').text = 'Ground condition'
#
## status
# status = ET.SubElement(idinfo, 'status')
# ET.SubElement(status, 'progress').text = 'Complete'
# ET.SubElement(status, 'update').text = 'As needed'
#
## extent
# extent = ET.SubElement(idinfo, 'spdom')
# bounding = ET.SubElement(extent, 'bounding')
# for name in ['westbc', 'eastbc', 'northbc', 'southbc']:
#    ET.SubElement(bounding, name).text = '{0:.1f}'.format(survey_extent[name[:-2]])
#
#### keywords
# keywords = ET.SubElement(idinfo, 'keywords')
# t1 = ET.SubElement(keywords, 'theme')
# ET.SubElement(t1, 'themekt').text = 'None'
# for kw in keywords_general:
#    ET.SubElement(t1, 'themekey').text = kw
#
## categories
# t2 = ET.SubElement(keywords, 'theme')
# ET.SubElement(t2, 'themkt').text = 'ISO 19115 Topic Categories'
# ET.SubElement(t2, 'themekey').text = 'GeoscientificInformation'
#
## USGS thesaurus
# t3 = ET.SubElement(keywords, 'theme')
# ET.SubElement(t3, 'themekt').text = 'USGS Thesaurus'
# for kw in keywords_thesaurus:
#    ET.SubElement(t3, 'themekey').text = kw
#
## places
# place = ET.SubElement(keywords, 'place')
# ET.SubElement(place, 'placekt').text = 'Geographic Names Information System (GNIS)'
# for loc in locations:
#    ET.SubElement(place, 'placekey').text = loc
#
### constraints
# ET.SubElement(idinfo, 'accconst').text = 'None'
# ET.SubElement(idinfo, 'useconst').text = use_constraint
#
#### contact information
# ptcontact = ET.SubElement(idinfo, 'ptcontac')
# contact_info = ET.SubElement(ptcontact, 'cntinfo')
# c_perp = ET.SubElement(contact_info, 'cntperp')
# ET.SubElement(c_perp, 'cntper').text = submitter['name']
# ET.SubElement(c_perp, 'cntorg').text = submitter['org']
# c_address = ET.SubElement(contact_info, 'cntaddr')
# ET.SubElement(c_address, 'addrtype').text = 'Mailing and physical'
# for key in ['address', 'city', 'state', 'postal', 'country']:
#    ET.SubElement(c_address, key).text = submitter[key]
#
# ET.SubElement(contact_info, 'cntvoice').text = submitter['phone']
# ET.SubElement(contact_info, 'cntemail').text = submitter['email']
## funding source
# ET.SubElement(idinfo, 'datacred').text = funding_source
#
## =============================================================================
## Data quality
## =============================================================================
# data_quality = ET.SubElement(metadata, 'dataqual')
#
# accuracy = ET.SubElement(data_quality, 'attracc')
# ET.SubElement(accuracy, 'attraccr').text = 'No formal attribute accuracy '+\
#                                           'tests were conducted.'
# ET.SubElement(data_quality, 'logic').text = 'No formal logical accuracy tests'+\
#                                            ' were conducted.'
# ET.SubElement(data_quality, 'complete').text = complete_warning
#
## accuracy
# position_acc = ET.SubElement(data_quality, 'posacc')
# h_acc = ET.SubElement(position_acc, 'horizpa')
# ET.SubElement(h_acc, 'horizpar').text = horizonal_acc
# v_acc = ET.SubElement(position_acc, 'vertacc')
# ET.SubElement(v_acc, 'vertaccr').text = vert_acc
#
## lineage
# lineage = ET.SubElement(data_quality, 'lineage')
# processing_step_01 = ET.SubElement(lineage, 'procstep')
# ET.SubElement(processing_step_01, 'procdesc').text = processing
# ET.SubElement(processing_step_01, 'procdate').text = year
## =============================================================================
## Spatial reference
## =============================================================================
# spref = ET.SubElement(metadata, 'spref')
#
# horizontal_sys = ET.SubElement(spref, 'horizontal_sys')
# h_geographic = ET.SubElement(horizontal_sys, 'geograph')
# ET.SubElement(h_geographic, 'latres').text = '0.0197305745'
# ET.SubElement(h_geographic, 'longres').text = '0.0273088247'
# ET.SubElement(h_geographic, 'geogunit').text = 'Decimal seconds'
#
# h_geodetic = ET.SubElement(horizontal_sys, 'geodetic')
# ET.SubElement(h_geodetic, 'horizdn').text = 'D_WGS_1984'
# ET.SubElement(h_geodetic, 'ellips').text = 'WGS_1984'
# ET.SubElement(h_geodetic, 'semiaxis').text = '6378137.0'
# ET.SubElement(h_geodetic, 'denflat').text = '298.257223563'
#
## =============================================================================
##
## =============================================================================
# eainfo = ET.SubElement(metadata, 'eainfo')
#
# overview = ET.SubElement(eainfo, 'overview')
# ET.SubElement(overview, 'eaover').text = guide_pdf_fn
# ET.SubElement(overview, 'eadetcit').text = guide_description
#
# overview_02 = ET.SubElement(eainfo, 'overview')
# ET.SubElement(overview_02, 'eaover').text = dictionary_fn
# ET.SubElement(overview_02, 'eadetcit').text = dictionary_description
#
# detailed = ET.SubElement(eainfo, 'detailed')
# entry_type = ET.SubElement(detailed, 'enttyp')
# ET.SubElement(entry_type, 'enttypl').text = shapefile_fn
# ET.SubElement(entry_type, 'enttypd').text = shapefile_description
# ET.SubElement(entry_type, 'enttrypds').text = usgs_str
#
# entry_attr = ET.SubElement(detailed, 'attr')
# ET.SubElement(entry_attr, 'attrlabl').text = 'Station'
# ET.SubElement(entry_attr, 'attrdef').text = 'Individual station name within MT survey.'
# ET.SubElement(entry_attr, 'attrdefs').text = usgs_str
# entry_attr_dom = ET.SubElement(entry_attr, 'attrdomv')
# ET.SubElement(entry_attr_dom, 'udom').text = 'Station identifier of MT '+\
#                                             'sounding used to distinguish '+\
#                                             'between the soundings associated '+\
#                                             'with this survey.'
#
# lat_attr = ET.SubElement(detailed, 'attr')
# ET.SubElement(lat_attr, 'attrlabl').text = 'Lat_WGS84'
# ET.SubElement(lat_attr, 'attrdef').text = 'Latitude coordinate of station, '+\
#                                          'referenced to the World Geodetic '+\
#                                          'Service Datum of 1984 (WGS84).'
# ET.SubElement(lat_attr, 'attrdefs').text = usgs_str
# lat_dom = ET.SubElement(lat_attr, 'attrdomv')
# lat_rdom = ET.SubElement(lat_dom, 'rdom')
# ET.SubElement(lat_rdom, 'dommin').text = '{0:.1f}'.format(survey_extent['south'])
# ET.SubElement(lat_rdom, 'dommax').text = '{0:.1f}'.format(survey_extent['north'])
# ET.SubElement(lat_rdom, 'attrunit').text = 'Decimal degrees'
#
# lon_attr = ET.SubElement(detailed, 'attr')
# ET.SubElement(lon_attr, 'attrlabl').text = 'Lon_WGS84'
# ET.SubElement(lon_attr, 'attrdef').text = 'Longitude coordinate of station, '+\
#                                          'referenced to the World Geodetic '+\
#                                          'Service Datum of 1984 (WGS84).'
# ET.SubElement(lon_attr, 'attrdefs').text = usgs_str
# lon_dom = ET.SubElement(lon_attr, 'attrdomv')
# lon_rdom = ET.SubElement(lon_dom, 'rdom')
# ET.SubElement(lon_rdom, 'dommin').text = '{0:.1f}'.format(survey_extent['west'])
# ET.SubElement(lon_rdom, 'dommax').text = '{0:.1f}'.format(survey_extent['east'])
# ET.SubElement(lon_rdom, 'attrunit').text = 'Decimal degrees'
#
# elev_attr = ET.SubElement(detailed, 'attr')
# ET.SubElement(elev_attr, 'attrlabl').text = 'Elev_NAVD88'
# ET.SubElement(elev_attr, 'attrdef').text = 'Elevation, referenced to the North '+\
#                                            'American Vertical Datum of 1988 '+\
#                                            '(NAVD 88)'
# ET.SubElement(elev_attr, 'attrdefs').text = usgs_str
# elev_dom = ET.SubElement(elev_attr, 'attrdomv')
# elev_rdom = ET.SubElement(elev_dom, 'rdom')
# ET.SubElement(elev_rdom, 'dommin').text = '{0:.0f}'.format(survey_extent['elev_min'])
# ET.SubElement(elev_rdom, 'dommax').text = '{0:.0f}'.format(survey_extent['elev_max'])
# ET.SubElement(elev_rdom, 'attrunit').text = 'Meters'
#
## =============================================================================
## Distribution Info
## =============================================================================
# distinfo = ET.SubElement(metadata, 'distinfo')
#
# distribute = ET.SubElement(distinfo, 'distrib')
# center_info = ET.SubElement(distribute, 'cntinfo')
# center_perp = ET.SubElement(center_info, 'cntperp')
# ET.SubElement(center_perp, 'cntper').text = science_base['name']
# ET.SubElement(center_perp, 'cntorg').text = science_base['org']
# center_address = ET.SubElement(center_info, 'cntaddr')
# ET.SubElement(center_address, 'addrtype').text = 'Mailing and physical'
# for key in ['address', 'city', 'state', 'postal', 'country']:
#    ET.SubElement(center_address, key).text = science_base[key]
# ET.SubElement(center_info, 'cntvoice').text = science_base['phone']
# ET.SubElement(center_info, 'cntemail').text = science_base['email']
# ET.SubElement(distinfo, 'disliab').text = science_base['liability']
#
## =============================================================================
## Meta info
## =============================================================================
# metainfo = ET.SubElement(metadata, 'metainfo')
#
# ET.SubElement(metainfo, 'metd').text = datetime.datetime.now().strftime('%Y%m%d')
# meta_center = ET.SubElement(metainfo, 'metc')
#
#### contact information
# meta_contact = ET.SubElement(meta_center, 'cntinfo')
# meta_perp = ET.SubElement(meta_contact, 'cntperp')
# ET.SubElement(meta_contact, 'cntos').text = submitter['position']
# ET.SubElement(meta_perp, 'cntper').text = submitter['name']
# ET.SubElement(meta_perp, 'cntorg').text = submitter['org']
# meta_address = ET.SubElement(meta_contact, 'cntaddr')
# ET.SubElement(meta_address, 'addrtype').text = 'Mailing and physical'
# for key in ['address', 'city', 'state', 'postal', 'country']:
#    ET.SubElement(meta_address, key).text = submitter[key]
#
# ET.SubElement(meta_contact, 'cntvoice').text = submitter['phone']
# ET.SubElement(meta_contact, 'cntemail').text = submitter['email']
#
# ET.SubElement(meta_contact, 'metastdn').text = 'Content Standard for Digital '+\
#                                                'Geospatial Metadata'
# ET.SubElement(meta_contact, 'metastdv').text = 'FGDC-STD-001-1998'
## =============================================================================
## write out xml
## =============================================================================
# xmlstr = minidom.parseString(ET.tostring(metadata, 'utf-8')).toprettyxml(indent="    ", encoding='UTF-8')
##with open(r"d:\Peacock\MTData\test.xml", 'w') as fid:
# with open(r"c:\Users\jpeacock\Documents\imush\test.xml", 'w') as fid:
#    fid.write(xmlstr)
