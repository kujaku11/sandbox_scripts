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
        self._author = None
        self.title = None
        self.journal = None
        self.date = None
        self.issue = None
        self.volume = None
        self.doi_url = None
        
    @property
    def author(self):
        return self._author
    
    @author.setter
    def author(self, author):
        if type(author) is not list:
            author = [author]
        self._author = author
        
class Survey(object):
    """
    data type to hold survey information
    """
    def __init__(self):
        self.begin_date = None
        self.end_date = None
        self._east = None
        self._west = None
        self._north = None
        self._south = None
        self._elev_min = None
        self._elev_max = None
        
    @property
    def east(self):
        return self._east
    @east.setter
    def east(self, east):
        self._east = float(east)
    
    @property
    def west(self):
        return self._west
    @west.setter
    def west(self, west):
        self._west = float(west)
        
    @property
    def north(self):
        return self._north
    @north.setter
    def north(self, north):
        self._north = float(north)
        
    @property
    def south(self):
        return self._south
    @south.setter
    def south(self, south):
        self._south = float(south)
    
    @property
    def elev_min(self):
        return self._elev_min
    @elev_min.setter
    def elev_min(self, elev_min):
        self._elev_min = float(elev_min)
        
    @property
    def elev_max(self):
        return self._elev_max
    @elev_max.setter
    def elev_max(self, elev_max):
        self._elev_max = float(elev_max)
        
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

        self.usgs_str = 'U.S. Geological Survey'
        self.xml_fn = None
        self.authors = None
        self.title = None
        self.doi_url = None
        self.journal_citation = Citation()
        self.purpose = None
        self.abstract = None
        self.supplement_info = None
        self.survey = Survey()
        self.submitter = Person()
        
        self.sc_dict = {'GGGSC': 'Geology, Geophysics, and Geochemistry Science Center',
                        'GMEGSC': 'Geology, Minerals, Energy, and Geophysics Science Center'}
        self.program_dict = {'MRP': 'Mineral Resources Program',
                             'VHP': 'Volcano Hazards Program'}
        
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
        
        self.udom = 'Station identifier of MT sounding used to distinguish '+\
                    'between the soundings associated with this survey.'
        self.lat_def = 'Latitude coordinate of station referenced to the '+\
                       'World Geodetic Service Datum of 1984 (WGS84).'
        self.lon_def = 'Longitude coordinate of station, referenced to the '+\
                       'World Geodetic Service Datum of 1984 (WGS84)'
        self.elev_def = 'Elevation, referenced to the North American '+\
                        'Vertical Datum of 1988 (NAVD 88)'
        
        self.metadata = ET.Element('metadata')
        
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
                 
    def read_config_file(self, config_fn):
        """
        Read in configuration file
        """
        # read in the configuration file
        with open(config_fn, 'r') as fid:
            lines = fid.readlines()
            
        for line in lines:
            # skip comment lines
            if line.find('#') == 0 or len(line.strip()) < 2:
                continue
            # make a key = value pair
            key, value = [item.strip() for item in line.split('=', 1)]
            if value == 'usgs_str':
                value = self.usgs_str
            if value.find('[') >= 0 and value.find(']') >= 0:
                value = value.replace('[', '').replace(']', '')
                value = [v.strip() for v in value.split(',')]
            
            # if there is a dot, meaning an object with an attribute separate 
            if key.find('.') > 0:
                obj, obj_attr = key.split('.')
                setattr(getattr(self, obj), obj_attr, value)
            else:
                setattr(self, key, value)
                
    def _assert_date_fmt(self, date):
        """
        Make sure that the date is in YYYYMMDD
        """
        date = date.replace('-', '')
        date = date.split(':', 1)[0]
        
        return date
                
    def _set_id_info(self):
        """
        set the ID information
        """
        idinfo = ET.SubElement(self.metadata, 'idinfo')
        
        citation = ET.SubElement(idinfo, 'citation')
        citeinfo = ET.SubElement(citation, 'citeinfo')
        for author in self.authors:
            ET.SubElement(citeinfo, 'origin').text = author
        ET.SubElement(citeinfo, 'pubdate').text = datetime.datetime.now().strftime('%Y')
        ET.SubElement(citeinfo, 'title').text = self.title
        ET.SubElement(citeinfo, 'geoform').text = 'ASCII, shapefile, image'
        
        pubinfo = ET.SubElement(citeinfo, 'pubinfo')
        ET.SubElement(pubinfo, 'pubplace').text = 'Denver, CO'
        ET.SubElement(pubinfo, 'publish').text = self.usgs_str 
        ET.SubElement(citeinfo, 'onlink').text = self.doi_url
        # journal publication
        if self.journal_citation:
            journal = ET.SubElement(citeinfo, 'lworkcit')
            jciteinfo = ET.SubElement(journal, 'citeinfo')
            for author in self.journal_citation.author:
                ET.SubElement(jciteinfo, 'origin').text = author
            ET.SubElement(jciteinfo, 'pubdate').text = self.journal_citation.date
            ET.SubElement(jciteinfo, 'title').text = self.journal_citation.title
            ET.SubElement(jciteinfo, 'geoform').text = 'Publication'
            serinfo = ET.SubElement(jciteinfo, 'serinfo')
            ET.SubElement(serinfo, 'sername').text = self.journal_citation.journal
            ET.SubElement(serinfo, 'issue').text = self.journal_citation.volume
            
            jpubinfo = ET.SubElement(jciteinfo, 'pubinfo')
            ET.SubElement(jpubinfo, 'pubplace').text = 'Denver, CO'
            ET.SubElement(jpubinfo, 'publish').text = self.usgs_str
            ET.SubElement(jciteinfo, 'onlink').text = self.journal_citation.doi_url
            
        # description
        description = ET.SubElement(idinfo, 'descript')
        ET.SubElement(description, 'abstract').text = self.abstract
        ET.SubElement(description, 'purpose').text = self.purpose
        ET.SubElement(description, 'supplinf').text = self.supplement_info
        
        # dates covered
        time_period = ET.SubElement(idinfo, 'timeperd')
        time_info = ET.SubElement(time_period, 'timeinfo')
        dates = ET.SubElement(time_info, 'rngdates')
        ET.SubElement(dates, 'begdate').text = self.survey.begin_date
        ET.SubElement(dates, 'enddate').text = self.survey.end_date
        ET.SubElement(time_info, 'current').text = 'Ground condition'
        
        # status
        status = ET.SubElement(idinfo, 'status')
        ET.SubElement(status, 'progress').text = 'Complete'
        ET.SubElement(status, 'update').text = 'As needed'
         
        # extent
        extent = ET.SubElement(idinfo, 'spdom')
        bounding = ET.SubElement(extent, 'bounding')
        for name in ['westbc', 'eastbc', 'northbc', 'southbc']:
            ET.SubElement(bounding, name).text = '{0:.1f}'.format(getattr(self.survey, 
                                                                         name[:-2]))
            
        ### keywords
        keywords = ET.SubElement(idinfo, 'keywords')
        t1 = ET.SubElement(keywords, 'theme')
        ET.SubElement(t1, 'themekt').text = 'None'
        for kw in self.keywords_general:
            ET.SubElement(t1, 'themekey').text = kw     
        
        # categories
        t2 = ET.SubElement(keywords, 'theme')
        ET.SubElement(t2, 'themkt').text = 'ISO 19115 Topic Categories'
        ET.SubElement(t2, 'themekey').text = 'GeoscientificInformation'
        
        # USGS thesaurus
        t3 = ET.SubElement(keywords, 'theme')
        ET.SubElement(t3, 'themekt').text = 'USGS Thesaurus'
        for kw in self.keywords_thesaurus:
            ET.SubElement(t3, 'themekey').text = kw
        
        # places
        place = ET.SubElement(keywords, 'place')
        ET.SubElement(place, 'placekt').text = 'Geographic Names Information System (GNIS)'
        for loc in self.locations:
            ET.SubElement(place, 'placekey').text = loc
            
        ## constraints
        ET.SubElement(idinfo, 'accconst').text = 'None'
        ET.SubElement(idinfo, 'useconst').text = self.use_constraint
        
        ### contact information
        ptcontact = ET.SubElement(idinfo, 'ptcontac')
        contact_info = ET.SubElement(ptcontact, 'cntinfo')
        c_perp = ET.SubElement(contact_info, 'cntperp')
        ET.SubElement(c_perp, 'cntper').text = self.submitter.name
        ET.SubElement(c_perp, 'cntorg').text = self.submitter.org
        c_address = ET.SubElement(contact_info, 'cntaddr')
        ET.SubElement(c_address, 'addrtype').text = 'Mailing and physical'
        for key in ['address', 'city', 'state', 'postal', 'country']:
            ET.SubElement(c_address, key).text = getattr(self.submitter, key)
        
        ET.SubElement(contact_info, 'cntvoice').text = self.submitter.phone
        ET.SubElement(contact_info, 'cntemail').text = self.submitter.email
        # funding source
        ET.SubElement(idinfo, 'datacred').text = self.submitter.funding_source
        
    def _set_data_quality(self):
        """
        Set data quality section
        """
        data_quality = ET.SubElement(self.metadata, 'dataqual')

        accuracy = ET.SubElement(data_quality, 'attracc')
        ET.SubElement(accuracy, 'attraccr').text = 'No formal attribute accuracy '+\
                                                   'tests were conducted.'
        ET.SubElement(data_quality, 'logic').text = 'No formal logical accuracy tests'+\
                                                    ' were conducted.'
        ET.SubElement(data_quality, 'complete').text = self.complete_warning
        
        # accuracy
        position_acc = ET.SubElement(data_quality, 'posacc')
        h_acc = ET.SubElement(position_acc, 'horizpa')
        ET.SubElement(h_acc, 'horizpar').text = self.horizontal_accuracy
        v_acc = ET.SubElement(position_acc, 'vertacc')
        ET.SubElement(v_acc, 'vertaccr').text = self.vertical_accuracy
        
        # lineage
        lineage = ET.SubElement(data_quality, 'lineage')
        step_num = len(self.processing.__dict__.keys())/2
        for step in range(1, step_num+1, 1):
            processing_step_01 = ET.SubElement(lineage, 'procstep')
            ET.SubElement(processing_step_01, 'procdesc').text = getattr(self.processing,
                                                                         'step_{0:02}'.format(step))
            ET.SubElement(processing_step_01, 'procdate').text = getattr(self.processing,
                                                                         'date_{0:02}'.format(step)) 
        
    def _set_spational_info(self):
        """
        set spatial information
        """
        spref = ET.SubElement(self.metadata, 'spref')
        
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
        
    def _set_extra_info(self):
        """
        set the extra info, still not sure what that stands for
        """
        eainfo = ET.SubElement(self.metadata, 'eainfo')
        
        overview = ET.SubElement(eainfo, 'overview')
        ET.SubElement(overview, 'eaover').text = self.guide.fn
        ET.SubElement(overview, 'eadetcit').text = self.guide.description
        
        overview_02 = ET.SubElement(eainfo, 'overview')
        ET.SubElement(overview_02, 'eaover').text = self.dictionary.fn
        ET.SubElement(overview_02, 'eadetcit').text = self.dictionary.description
        
        detailed = ET.SubElement(eainfo, 'detailed')
        entry_type = ET.SubElement(detailed, 'enttyp')
        ET.SubElement(entry_type, 'enttypl').text = self.shapefile.fn
        ET.SubElement(entry_type, 'enttypd').text = self.shapefile.description
        ET.SubElement(entry_type, 'enttrypds').text = self.usgs_str
        
        entry_attr = ET.SubElement(detailed, 'attr')
        ET.SubElement(entry_attr, 'attrlabl').text = 'Station'
        ET.SubElement(entry_attr, 'attrdef').text = 'Individual station name within MT survey.'
        ET.SubElement(entry_attr, 'attrdefs').text = self.usgs_str
        entry_attr_dom = ET.SubElement(entry_attr, 'attrdomv')
        ET.SubElement(entry_attr_dom, 'udom').text = self.udom 
        
        lat_attr = ET.SubElement(detailed, 'attr')
        ET.SubElement(lat_attr, 'attrlabl').text = 'Lat_WGS84'
        ET.SubElement(lat_attr, 'attrdef').text = self.lat_def
        ET.SubElement(lat_attr, 'attrdefs').text = self.usgs_str
        lat_dom = ET.SubElement(lat_attr, 'attrdomv')
        lat_rdom = ET.SubElement(lat_dom, 'rdom')
        ET.SubElement(lat_rdom, 'dommin').text = '{0:.1f}'.format(self.survey.south)
        ET.SubElement(lat_rdom, 'dommax').text = '{0:.1f}'.format(self.survey.north)
        ET.SubElement(lat_rdom, 'attrunit').text = 'Decimal degrees'
        
        lon_attr = ET.SubElement(detailed, 'attr')
        ET.SubElement(lon_attr, 'attrlabl').text = 'Lon_WGS84'
        ET.SubElement(lon_attr, 'attrdef').text = self.lon_def
        ET.SubElement(lon_attr, 'attrdefs').text = self.usgs_str
        lon_dom = ET.SubElement(lon_attr, 'attrdomv')
        lon_rdom = ET.SubElement(lon_dom, 'rdom')
        ET.SubElement(lon_rdom, 'dommin').text = '{0:.1f}'.format(self.survey.west)
        ET.SubElement(lon_rdom, 'dommax').text = '{0:.1f}'.format(self.survey.east)
        ET.SubElement(lon_rdom, 'attrunit').text = 'Decimal degrees'
        
        elev_attr = ET.SubElement(detailed, 'attr')
        ET.SubElement(elev_attr, 'attrlabl').text = 'Elev_NAVD88'
        ET.SubElement(elev_attr, 'attrdef').text = self.elev_def
        ET.SubElement(elev_attr, 'attrdefs').text = self.usgs_str
        elev_dom = ET.SubElement(elev_attr, 'attrdomv')
        elev_rdom = ET.SubElement(elev_dom, 'rdom')
        ET.SubElement(elev_rdom, 'dommin').text = '{0:.0f}'.format(self.survey.elev_min)
        ET.SubElement(elev_rdom, 'dommax').text = '{0:.0f}'.format(self.survey.elev_max)
        ET.SubElement(elev_rdom, 'attrunit').text = 'Meters'
        
    def _set_meta_info(self):
        """
        set the metadata info section
        """
        metainfo = ET.SubElement(self.metadata, 'metainfo')
        
        ET.SubElement(metainfo, 'metd').text = datetime.datetime.now().strftime('%Y%m%d')
        meta_center = ET.SubElement(metainfo, 'metc')
        
        ### contact information
        meta_contact = ET.SubElement(meta_center, 'cntinfo')
        meta_perp = ET.SubElement(meta_contact, 'cntperp')
        ET.SubElement(meta_contact, 'cntos').text = self.submitter.position
        ET.SubElement(meta_perp, 'cntper').text = self.submitter.name
        ET.SubElement(meta_perp, 'cntorg').text = self.submitter.org
        meta_address = ET.SubElement(meta_contact, 'cntaddr')
        ET.SubElement(meta_address, 'addrtype').text = 'Mailing and physical'
        for key in ['address', 'city', 'state', 'postal', 'country']:
            ET.SubElement(meta_address, key).text = getattr(self.submitter, key)
        
        ET.SubElement(meta_contact, 'cntvoice').text = self.submitter.phone
        ET.SubElement(meta_contact, 'cntemail').text = self.submitter.email
        
        ET.SubElement(meta_contact, 'metastdn').text = 'Content Standard for Digital '+\
                                                        'Geospatial Metadata'
        ET.SubElement(meta_contact, 'metastdv').text = 'FGDC-STD-001-1998'
#
    def write_xml_file(self, xml_fn):
        """
        write xml file
        """
        self.xml_fn = xml_fn
        
        self._set_id_info()
        self._set_data_quality()
        self._set_spational_info()
        self._set_extra_info()
        self._set_meta_info()
        
        # write the xml in a readable format
        xml_str = ET.tostring(self.metadata)
        xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ", 
                                                           encoding='UTF-8')
        with open(self.xml_fn, 'w') as fid:
            fid.write(xml_str)
# =============================================================================
# Test
# =============================================================================
cfg_fn = r"C:\Users\jpeacock\Documents\imush\xml_config_test.txt"

m = SurveyMetadata()
m.read_config_file(cfg_fn)
m.write_xml_file(r"c:\Users\jpeacock\Documents\imush\test.xml")

