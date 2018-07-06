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
usgs_str = 'U.S. Geological Survey'

authors = ['Jared R. Peacock', 'Kevin Denton', 'Dave Ponce']
year = '2018'
title = 'Magnetotelluric data from Mountain Pass, California'
doi_url = 'https://doi.org/10.5066/F7610XTR'
journal_citation = {'author': authors,
                    'title':title,
                    'journal':'Geosphere',
                    'date':'20190101',
                    'issue':'submitted',
                    'volume':'22',
                    'doi_url':'https://doi.org/10.5066/F7610XTR'}
abstract = 'abstract'
purpose = 'survey purpose'
supplement_info = 'in case something goes wrong or needs more explanation'
survey_begin = '20160505'
survey_end = '20160512'
survey_extent = {'west': -120,
                 'east': -118, 
                 'north': 39,
                 'south': 37,
                 'elev_min':0,
                 'elev_max':1500}

science_center = 'GMEGSC'
program = 'MRP'

sc_dict = {'GGGSC': 'Geology, Geophysics, and Geochemistry Science Center',
           'GMEGSC': 'Geology, Minerals, Energy, and Geophysics Science Center'}
program_dict = {'MRP': 'Mineral Resources Program',
               'VHP': 'Volcano Hazards Program'}

keywords_general = [sc_dict[science_center],
                    science_center,
                    program_dict[program],
                    program, 
                    'magnetotellurics',
                    'MT',
                    'time series',
                    'impedance',
                    'apparent resistivity',
                    'phase', 
                    'tipper']

keywords_thesaurus = ['Earth magnetic field',
                      'Geophysics',
                      'Electromagnetic surveying']

locations = ['Primm',
             'Mountain Pass']

use_constraint = 'There is no guarantee concerning the accuracy of the data. '+\
                 'Any user who modifies the data is obligated to describe the '+\
                 'types of modifications they perform. Data have been checked '+\
                 'to ensure the accuracy. If any errors are detected, please '+\
                 'notify the originating office. The U.S. Geological Survey '+\
                 'strongly recommends that careful attention be paid to the '+\
                 'metadata file associated with these data. Acknowledgment of '+\
                 'the U.S. Geological Survey would be appreciated in products '+\
                 'derived from these data. User specifically agrees not to '+\
                 'misrepresent the data, nor to imply that changes made were '+\
                 'approved or endorsed by the U.S. Geological Survey. Please '+\
                 'refer to https://www2.usgs.gov/laws/privacy.html for the '+\
                 'USGS disclaimer.'
                 
submitter = {'name': 'Jared R. Peacock',
             'org': 'U.S. Geological Survey',
             'address': 'Bldg 2, MS 989, 345 Middlefield Rd.',
             'city': 'Menlo Park',
             'state': 'CA',
             'postal': '94125',
             'phone':'650-329-4833',
             'email': 'jpeacock@usgs.gov',
             'country': 'USA',
             'position': 'Research Geophysicist'}

science_base = {'name': 'Science Base',
                'org': usgs_str,
                'address': 'Building 810, Mail Stop 302, Denver Federal Center',
                'city': 'Denver',
                'state': 'CO',
                'postal': '80255',
                'phone':'1-888-275-8747',
                'email': 'sciencebase@usgs.gov',
                'country': 'USA',
                'liability': 'Unless otherwise stated, all data, metadata and '+\
                             'related materials are considered to satisfy the '+\
                             'quality standards relative to the purpose for '+\
                             'which the data were collected. Although these '+\
                             'data and associated metadata have been reviewed '+\
                             'for accuracy and completeness and approved for '+\
                             'release by the U.S. Geological Survey (USGS), '+\
                             'no warranty expressed or implied is made '+\
                             'regarding the display or utility of the data for '+\
                             'other purposes, nor on all computer systems, nor '+\
                             'shall the act of distribution constitute any such '+\
                             'warranty.'}

funding_source = 'Mineral Resources Program'

complete_warning = 'Data set is considered complete for the information '+\
                   'presented, as described in the abstract. Users are '+\
                   'advised to read the rest of the metadata record '+\
                   'carefully for additional details.'
                   
horizonal_acc = 'Spatial locations were determined from hand-held global '+\
                'positioning system (GPS) devices. In general, the GPS units '+\
                'used by field scientists recorded sample locations to '+\
                'within 100 feet (30 meters) of the true location. The '+\
                'locations were verified using a geographic information '+\
                'system (GIS) and digital topographic maps.'
                
vert_acc = 'Elevations were determined from USGS, The National Map, Bulk '+\
           'Point Query Service based on the USGS 3DEP (3D elevation program) '+\
           '1/3 arc-second layer (10-meter). Vertical accuracy was not '+\
           'assessed for this specific dataset. The overall absolute '+\
           'vertical accuracy of the seamless DEMs within the conterminous '+\
           'United States (2013), expressed as the root mean square error '+\
           '(RMSE) of 25,310 reference points, was 1.55 meters (USGS, '+\
           '2014 - http://dx.doi.org/10.3133/ofr20141008). The vertical '+\
           'accuracy varies across the U.S. as a result of differences in '+\
           'source DEM quality, terrain relief, land cover, and other factors.'

processing = 'The transfer function estimates provided in the *.edi files and '+\
            'displayed in the *.png file were constructed by selecting '+\
            'optimal TF estimates at each period from a suite of data runs. '+\
            'High (500 Hz), mid (50 Hz), and low (6.25 Hz) frequency broadband '+\
            'recordings provided TF estimates for 10-100 Hz, 1-10 Hz, and '+\
            '0.001-1 Hz, respectively. Where available, long period (8 Hz) MT'+\
            'recordings provided TF estimates for periods from 0.001-0.1 Hz '+\
            '(10-11,000 seconds). A select few stations have only long period'+\
            'recordings available, in which case TF estimates are provided for'+\
            'periods 0.001-1 Hz. So-called optimal TFs were selected based on'+\
            'examination of phase slope, smooth curve assumptions, and '+\
            'operator discretion.'
            
guide_pdf_fn = 'Guide_MT_Data.pdf'
guide_description = 'Description of available magnetotelluric data types '+\
                    'from U.S. Geological Survey. This report describes '+\
                    'typical magnetotelluric instrumentation and the various'+\
                    'data types required in MT processing and data quality'+\
                    'assessment (including electric and magnetic field '+\
                    'time-series, instrument response files, and transfer '+\
                    'functions), accessible at, '+\
                    'https://www.sciencebase.gov/catalog/file/get/59400c59e4b0764e6c631120?name=Guide_to_Magnetotelluric_Data_Types.pdf'
                    
dictionary_fn = 'MT_Dictionary.csv'
dictionary_description = 'A data dictionary describing the entity and '+\
                         'attributes of magnetotelluric data files produced'+\
                         'by data acquisition and processing of '+\
                         'magnetotelluric data using NIMS long-period and '+\
                         'Electromagnetic Instruments MT24 broadband '+\
                         'magnetotelluric instrumetation, accessible at, '+\
                         'https://www.sciencebase.gov/catalog/file/get/59400c59e4b0764e6c631120?name=MT_DataDictionary.csv.'
                         
shapefile_fn = 'shapefile.shp'
shapefile_description = 'Table containing attribute information associated '+\
                        'with the data set.'

# =============================================================================
# main element
# =============================================================================
metadata = ET.Element('metadata')

# =============================================================================
# ID information
# =============================================================================
idinfo = ET.SubElement(metadata, 'idinfo')

citation = ET.SubElement(idinfo, 'citation')
citeinfo = ET.SubElement(citation, 'citeinfo')
for author in authors:
    ET.SubElement(citeinfo, 'origin').text = author
ET.SubElement(citeinfo, 'pubdate').text = year
ET.SubElement(citeinfo, 'title').text = title
ET.SubElement(citeinfo, 'geoform').text = 'ASCII, shapefile, image'

pubinfo = ET.SubElement(citeinfo, 'pubinfo')
ET.SubElement(pubinfo, 'pubplace').text = 'Menlo Park, CA'
ET.SubElement(pubinfo, 'publish').text = usgs_str 

ET.SubElement(citeinfo, 'onlink').text = doi_url
# journal publication
if journal_citation:
    journal = ET.SubElement(citeinfo, 'lworkcit')
    jciteinfo = ET.SubElement(journal, 'citeinfo')
    for author in journal_citation['author']:
        ET.SubElement(jciteinfo, 'origin').text = author
    ET.SubElement(jciteinfo, 'pubdate').text = journal_citation['date']
    ET.SubElement(jciteinfo, 'title').text = journal_citation['title']
    ET.SubElement(jciteinfo, 'geoform').text = 'Publication'
    serinfo = ET.SubElement(jciteinfo, 'serinfo')
    ET.SubElement(serinfo, 'sername').text = journal_citation['journal']
    ET.SubElement(serinfo, 'issue').text = journal_citation['volume']
    
    jpubinfo = ET.SubElement(jciteinfo, 'pubinfo')
    ET.SubElement(jpubinfo, 'pubplace').text = 'Menlo Park, CA'
    ET.SubElement(jpubinfo, 'publish').text = usgs_str
    
    ET.SubElement(jciteinfo, 'onlink').text = journal_citation['doi_url']
    
# description
description = ET.SubElement(idinfo, 'descript')
ET.SubElement(description, 'abstract').text = abstract
ET.SubElement(description, 'purpose').text = purpose
ET.SubElement(description, 'supplinf').text = supplement_info

# dates covered
time_period = ET.SubElement(idinfo, 'timeperd')
time_info = ET.SubElement(time_period, 'timeinfo')
dates = ET.SubElement(time_info, 'rngdates')
ET.SubElement(dates, 'begdate').text = survey_begin
ET.SubElement(dates, 'enddate').text = survey_end
ET.SubElement(time_info, 'current').text = 'Ground condition'

# status
status = ET.SubElement(idinfo, 'status')
ET.SubElement(status, 'progress').text = 'Complete'
ET.SubElement(status, 'update').text = 'As needed'
 
# extent
extent = ET.SubElement(idinfo, 'spdom')
bounding = ET.SubElement(extent, 'bounding')
for name in ['westbc', 'eastbc', 'northbc', 'southbc']:
    ET.SubElement(bounding, name).text = '{0:.1f}'.format(survey_extent[name[:-2]])
    
### keywords
keywords = ET.SubElement(idinfo, 'keywords')
t1 = ET.SubElement(keywords, 'theme')
ET.SubElement(t1, 'themekt').text = 'None'
for kw in keywords_general:
    ET.SubElement(t1, 'themekey').text = kw     

# categories
t2 = ET.SubElement(keywords, 'theme')
ET.SubElement(t2, 'themkt').text = 'ISO 19115 Topic Categories'
ET.SubElement(t2, 'themekey').text = 'GeoscientificInformation'

# USGS thesaurus
t3 = ET.SubElement(keywords, 'theme')
ET.SubElement(t3, 'themekt').text = 'USGS Thesaurus'
for kw in keywords_thesaurus:
    ET.SubElement(t3, 'themekey').text = kw

# places
place = ET.SubElement(keywords, 'place')
ET.SubElement(place, 'placekt').text = 'Geographic Names Information System (GNIS)'
for loc in locations:
    ET.SubElement(place, 'placekey').text = loc
    
## constraints
ET.SubElement(idinfo, 'accconst').text = 'None'
ET.SubElement(idinfo, 'useconst').text = use_constraint

### contact information
ptcontact = ET.SubElement(idinfo, 'ptcontac')
contact_info = ET.SubElement(ptcontact, 'cntinfo')
c_perp = ET.SubElement(contact_info, 'cntperp')
ET.SubElement(c_perp, 'cntper').text = submitter['name']
ET.SubElement(c_perp, 'cntorg').text = submitter['org']
c_address = ET.SubElement(contact_info, 'cntaddr')
ET.SubElement(c_address, 'addrtype').text = 'Mailing and physical'
for key in ['address', 'city', 'state', 'postal', 'country']:
    ET.SubElement(c_address, key).text = submitter[key]

ET.SubElement(contact_info, 'cntvoice').text = submitter['phone']
ET.SubElement(contact_info, 'cntemail').text = submitter['email']
# funding source
ET.SubElement(idinfo, 'datacred').text = funding_source

# =============================================================================
# Data quality
# =============================================================================
data_quality = ET.SubElement(metadata, 'dataqual')

accuracy = ET.SubElement(data_quality, 'attracc')
ET.SubElement(accuracy, 'attraccr').text = 'No formal attribute accuracy '+\
                                           'tests were conducted.'
ET.SubElement(data_quality, 'logic').text = 'No formal logical accuracy tests'+\
                                            ' were conducted.'
ET.SubElement(data_quality, 'complete').text = complete_warning

# accuracy
position_acc = ET.SubElement(data_quality, 'posacc')
h_acc = ET.SubElement(position_acc, 'horizpa')
ET.SubElement(h_acc, 'horizpar').text = horizonal_acc
v_acc = ET.SubElement(position_acc, 'vertacc')
ET.SubElement(v_acc, 'vertaccr').text = vert_acc

# lineage
lineage = ET.SubElement(data_quality, 'lineage')
processing_step_01 = ET.SubElement(lineage, 'procstep')
ET.SubElement(processing_step_01, 'procdesc').text = processing
ET.SubElement(processing_step_01, 'procdate').text = year 
# =============================================================================
# Spatial reference
# =============================================================================
spref = ET.SubElement(metadata, 'spref')

horizontal_sys = ET.SubElement(spref, 'horizontal_sys')
h_geographic = ET.SubElement(horizontal_sys, 'geograph')
ET.SubElement(h_geographic, 'latres').text = '0.0197305745'
ET.SubElement(h_geographic, 'longres').text = '0.0273088247'
ET.SubElement(h_geographic, 'geogunit').text = 'Decimal seconds'

h_geodetic = ET.SubElement(horizontal_sys, 'geodetic')
ET.SubElement(h_geodetic, 'horizdn').text = 'D_WGS_1984'
ET.SubElement(h_geodetic, 'ellips').text = 'WGS_1984'
ET.SubElement(h_geodetic, 'semiaxis').text = '6378137.0'
ET.SubElement(h_geodetic, 'denflat').text = '298.257223563'

# =============================================================================
# 
# =============================================================================
eainfo = ET.SubElement(metadata, 'eainfo')

overview = ET.SubElement(eainfo, 'overview')
ET.SubElement(overview, 'eaover').text = guide_pdf_fn
ET.SubElement(overview, 'eadetcit').text = guide_description

overview_02 = ET.SubElement(eainfo, 'overview')
ET.SubElement(overview_02, 'eaover').text = dictionary_fn
ET.SubElement(overview_02, 'eadetcit').text = dictionary_description

detailed = ET.SubElement(eainfo, 'detailed')
entry_type = ET.SubElement(detailed, 'enttyp')
ET.SubElement(entry_type, 'enttypl').text = shapefile_fn
ET.SubElement(entry_type, 'enttypd').text = shapefile_description
ET.SubElement(entry_type, 'enttrypds').text = usgs_str

entry_attr = ET.SubElement(detailed, 'attr')
ET.SubElement(entry_attr, 'attrlabl').text = 'Station'
ET.SubElement(entry_attr, 'attrdef').text = 'Individual station name within MT survey.'
ET.SubElement(entry_attr, 'attrdefs').text = usgs_str
entry_attr_dom = ET.SubElement(entry_attr, 'attrdomv')
ET.SubElement(entry_attr_dom, 'udom').text = 'Station identifier of MT '+\
                                             'sounding used to distinguish '+\
                                             'between the soundings associated '+\
                                             'with this survey.' 

lat_attr = ET.SubElement(detailed, 'attr')
ET.SubElement(lat_attr, 'attrlabl').text = 'Lat_WGS84'
ET.SubElement(lat_attr, 'attrdef').text = 'Latitude coordinate of station, '+\
                                          'referenced to the World Geodetic '+\
                                          'Service Datum of 1984 (WGS84).'
ET.SubElement(lat_attr, 'attrdefs').text = usgs_str
lat_dom = ET.SubElement(lat_attr, 'attrdomv')
lat_rdom = ET.SubElement(lat_dom, 'rdom')
ET.SubElement(lat_rdom, 'dommin').text = '{0:.1f}'.format(survey_extent['south'])
ET.SubElement(lat_rdom, 'dommax').text = '{0:.1f}'.format(survey_extent['north'])
ET.SubElement(lat_rdom, 'attrunit').text = 'Decimal degrees'

lon_attr = ET.SubElement(detailed, 'attr')
ET.SubElement(lon_attr, 'attrlabl').text = 'Lon_WGS84'
ET.SubElement(lon_attr, 'attrdef').text = 'Longitude coordinate of station, '+\
                                          'referenced to the World Geodetic '+\
                                          'Service Datum of 1984 (WGS84).'
ET.SubElement(lon_attr, 'attrdefs').text = usgs_str
lon_dom = ET.SubElement(lon_attr, 'attrdomv')
lon_rdom = ET.SubElement(lon_dom, 'rdom')
ET.SubElement(lon_rdom, 'dommin').text = '{0:.1f}'.format(survey_extent['west'])
ET.SubElement(lon_rdom, 'dommax').text = '{0:.1f}'.format(survey_extent['east'])
ET.SubElement(lon_rdom, 'attrunit').text = 'Decimal degrees'

elev_attr = ET.SubElement(detailed, 'attr')
ET.SubElement(elev_attr, 'attrlabl').text = 'Elev_NAVD88'
ET.SubElement(elev_attr, 'attrdef').text = 'Elevation, referenced to the North '+\
                                            'American Vertical Datum of 1988 '+\
                                            '(NAVD 88)'
ET.SubElement(elev_attr, 'attrdefs').text = usgs_str
elev_dom = ET.SubElement(elev_attr, 'attrdomv')
elev_rdom = ET.SubElement(elev_dom, 'rdom')
ET.SubElement(elev_rdom, 'dommin').text = '{0:.0f}'.format(survey_extent['elev_min'])
ET.SubElement(elev_rdom, 'dommax').text = '{0:.0f}'.format(survey_extent['elev_max'])
ET.SubElement(elev_rdom, 'attrunit').text = 'Meters'

# =============================================================================
# Distribution Info
# =============================================================================
distinfo = ET.SubElement(metadata, 'distinfo')

distribute = ET.SubElement(distinfo, 'distrib')
center_info = ET.SubElement(distribute, 'cntinfo')
center_perp = ET.SubElement(center_info, 'cntperp')
ET.SubElement(center_perp, 'cntper').text = science_base['name']
ET.SubElement(center_perp, 'cntorg').text = science_base['org']
center_address = ET.SubElement(center_info, 'cntaddr')
ET.SubElement(center_address, 'addrtype').text = 'Mailing and physical'
for key in ['address', 'city', 'state', 'postal', 'country']:
    ET.SubElement(center_address, key).text = science_base[key]
ET.SubElement(center_info, 'cntvoice').text = science_base['phone']
ET.SubElement(center_info, 'cntemail').text = science_base['email']
ET.SubElement(distinfo, 'disliab').text = science_base['liability']

# =============================================================================
# Meta info
# =============================================================================
metainfo = ET.SubElement(metadata, 'metainfo')

ET.SubElement(metainfo, 'metd').text = datetime.datetime.now().strftime('%Y%m%d')
meta_center = ET.SubElement(metainfo, 'metc')

### contact information
meta_contact = ET.SubElement(meta_center, 'cntinfo')
meta_perp = ET.SubElement(meta_contact, 'cntperp')
ET.SubElement(meta_contact, 'cntos').text = submitter['position']
ET.SubElement(meta_perp, 'cntper').text = submitter['name']
ET.SubElement(meta_perp, 'cntorg').text = submitter['org']
meta_address = ET.SubElement(meta_contact, 'cntaddr')
ET.SubElement(meta_address, 'addrtype').text = 'Mailing and physical'
for key in ['address', 'city', 'state', 'postal', 'country']:
    ET.SubElement(meta_address, key).text = submitter[key]

ET.SubElement(meta_contact, 'cntvoice').text = submitter['phone']
ET.SubElement(meta_contact, 'cntemail').text = submitter['email']

ET.SubElement(meta_contact, 'metastdn').text = 'Content Standard for Digital '+\
                                                'Geospatial Metadata'
ET.SubElement(meta_contact, 'metastdv').text = 'FGDC-STD-001-1998'
# =============================================================================
# write out xml
# =============================================================================
xmlstr = minidom.parseString(ET.tostring(metadata, 'utf-8')).toprettyxml(indent="    ", encoding='UTF-8')
#with open(r"d:\Peacock\MTData\test.xml", 'w') as fid:
with open(r"c:\Users\jpeacock\Documents\imush\test.xml", 'w') as fid:
    fid.write(xmlstr)