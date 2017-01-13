# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 16:39:40 2017

@author: jpeacock
"""

import os
import mtpy.core.mt as mt
import xml.etree.ElementTree as ET
import datetime
from xml.dom import minidom

dt_fmt = '%Y-%m-%dT%H:%M:%S'
#==============================================================================
# Inputs
#==============================================================================
edi_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\EDI_Files_birrp_mshs\Rotated_m18_deg\ms11.edi"
cfg_fn = r"C:\Users\jpeacock\Documents\PyScripts\xml_cfg_test.cfg"


class Dummy(object):
    def __init__(self, **kwargs):
        
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

conditions_of_use = "All data and metadata for this survey are available free \
                     of charge and may be copied freely, duplicated and further\
                     distributed provided this data set is cited as the\
                     reference. While the author(s) strive to provide data and \
                     metadata of best possible quality, neither the author(s) \
                     of this data set, not IRIS make any claims, promises, or \
                     guarantees about the accuracy, completeness, or adequacy \
                     of this information, and expressly disclaim liability for\
                     errors and omissions in the contents of this file. \
                     Guidelines about the quality or limitations of the data \
                     and metadata, as obtained from the author(s), are \
                     included for informational purposes only."
                     
estimates = [Dummy(**{'_name':'Estimate(type=real)(name=VAR)',
                      'Description':'Variance',
                       'ExternalURL':None,
                       'Intention':'error estimate',
                       'Tag':'variance'}),
             Dummy(**{'_name':'Estimate(type=complex)(name=COV)',
                      'Description':'Full covariance between each two TF components',
                      'ExternalURL':None,
                      'Intention':'error estimate',
                      'Tag':'covariance'}),
             Dummy(**{'_name':'Estimate(type=complex)(name=INVSIGCOV)',
                       'Description':'Inverse Coheren Signal Power Matrix S',
                       'ExternalURL':None,
                       'Intention':'signal power estimate',
                       'Tag':'inverse_signal_covariance'}),
              Dummy(**{'_name':'Estimate(type=complex)(name=RESIDCOV)',
                       'Description':'Residual Covariance N',
                       'ExternalURL':None,
                       'Intention':'error estimate',
                       'Tag':'residual_covariance'}),
              Dummy(**{'_name':'Estimate(type=complex)(name=COH)',
                       'Description':'Coherence',
                       'ExternalURL':None,
                       'Intention':'signal coherence',
                       'Tag':'coherence'}),
              Dummy(**{'_name':'Estimate(type=complex)(name=PREDCOH)',
                       'Description':'Multiple Coherence',
                       'ExternalURL':None,
                       'Intention':'signal coherence',
                       'Tag':'multiple_coherence'}),
              Dummy(**{'_name':'Estimate(type=complex)(name=SIGAMP)',
                       'Description':'Signal Amplitude',
                       'ExternalURL':None,
                       'Intention':'signal power estimate',
                       'Tag':'signal_amplitude'}),
              Dummy(**{'_name':'Estimate(type=complex)(name=SIGNOISE)',
                       'Description':'Signal Noise',
                       'ExternalURL':None,
                       'Intention':'error estimate',
                       'Tag':'signal_noise'})]
                       
data_types = [Dummy(**{'_name':'DataType(units=[mV/km]/[nT])(type=complex)(name=Z)(input=H)(output=E)',
                       'Description':'MT impedance',
                       'ExternalURL':None,
                       'Intention':'primary data type',
                       'Tag':'impedance'}),
              Dummy(**{'_name':'DataType(units=[])(type=complex)(name=T)(input=H)(output=H)',
                       'Description':'Tipper-Vertical Field Transfer Function',
                       'ExternalURL':None,
                       'Intention':'primary data type',
                       'Tag':'tipper'})]
#==============================================================================
# Useful Functions
#==============================================================================                
class XML_Config(object):
    """
    class to deal with configuration files for xml
    """    
    
    def __init__(self, **kwargs):
        self.cfg_fn = None
        self.cfg_dict = None
        
        # Initialize the default attributes and values
        self.Description = 'Magnetotelluric Transfer Functions'
        self.ProductID = None
        self.Project = None
        self.Survey = None
        self.Country = None
        self.SubType = 'MT_TF'
        self.Notes = None
        self.Tags = 'impedance, tipper'
        
        self.Image = Dummy(**{'PrimaryData':None,
                              'Filename':None,
                              '_name':'Image'})
                              
        self.Original = Dummy(**{'Attachment':None,
                                 'Filename':None,
                                 '_name':'Original'})
        
        self.TimeSeriesArchived = Dummy(**{'Value':0, 
                                           'URL':None,
                                           '_name':'TimeSeriesArchived'})
        self.ExternalURL = Dummy(**{'Description':None,
                                    'URL':None,
                                    '_name':'ExternalURL'})
        self.PrimaryData = Dummy(**{'Filename':None,
                                    'GroupKey':0,
                                    'OrderKey':0,
                                    '_name':'PrimaryData'})
                                    
        self.Attachment = Dummy(**{'Filename':None,
                                   'Description':'Original file use to produce XML',
                                   '_name':'Attachment'})
                                   
        
        self.Provenance = Dummy(**{'CreatTime':datetime.datetime.strftime(
                                               datetime.datetime.utcnow(), 
                                               dt_fmt),
                                    'CreatingApplication':'MTpy.core.xml',
                                    'Submitter':Dummy(**{'Name':None,
                                                         'Email':None,
                                                         'Org':None,
                                                         'OrgURL':None,
                                                         '_name':'Submitter'}),
                                    'Creator':Dummy(**{'Name':None,
                                                       'Email':None,
                                                       'Org':None,
                                                       'OrgURL':None,
                                                       '_name':'Creator'}),
                                    '_name':'Provenance'})
                                                       
        self.Copyright = Dummy(**{'Citation':Dummy(**{'Title':None,
                                                      'Authors':None,
                                                      'Year':None,
                                                      'Journal':None,
                                                      'Volume':None,
                                                      'DOI':None,
                                                      '_name':'Citation'}),
                                  'ReleaseStatus':'Closed',
                                  'ConditionsOfUse':conditions_of_use,
                                  '_name':'Copyright'})
                                  
        self.ProcessingInfo = Dummy(**{'ProcessedBy':None,
                                       'ProcessingSoftware':Dummy(**{'Name':None,
                                                                     'LastMod':None,
                                                                     'Author':None,
                                                                     '_name':'ProcessingSoftware'}),
                                        '_name':'ProcessingInfo'})
                                        
        self.Datum = None
        self.Declination = None
        
        self.Instrument = Dummy(**{'Type':None,
                                   'Manufacturer':None,
                                   'Id':None,
                                   'Settings':None,
                                   '_name':'Instrument'})

        self.Electrode = Dummy(**{'Type':None,
                                  'Manufacturer':None,
                                  'Id':None,
                                  '_name':'Electrode'})

        self.Magnetometer = Dummy(**{'Type':None,
                                     'Manufacturer':None,
                                     'Id':None,
                                     '_name':'Magnetometer'})
                                     
        self.DataQualityNotes = Dummy(**{'Rating':None,
                                         'GoodFromPeriod':None,
                                         'GoodToPeriod':None,
                                         'Comments':None,
                                         '_name':'DataQualityNotes'})
                                         
        self.DataQualityWarnings = Dummy(**{'Flag':0,
                                            'Comments':None,
                                            '_name':'DataQualityWarnings'})
                                            
        self.StatisticalEstimates = estimates
        self.DataTypes = data_types
                                   
        
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            
    def read_cfg_file(self, cfg_fn=None):
        if cfg_fn is not None:        
            self.cfg_fn = cfg_fn
            
        if not os.path.isfile(self.cfg_fn):
            raise NameError('Could not find {0}'.format(self.cfg_fn))
            
        with open(self.cfg_fn, 'r') as fid:
            lines = fid.readlines()
                        
        self.cfg_dict = {}    
        for line in lines:
            # skip comments
            if line[0] == '#':
                pass
            
            # skip blank lines
            elif line == '\n' or line == '\r':
                pass
            # else assume the line is metadata separated by = 
            else:
                line_list = line.strip().split('=')
                key = line_list[0].strip()
                value = line_list[1].strip()
                
                # if there is a dot then there is a tree of key words
                if key.find('.') > 0:
                    key_list = key.split('.')
                    if len(key_list) == 2:
                        setattr(getattr(self, key_list[0]), 
                                key_list[1], value)
                    elif len(key_list) == 3:
                        setattr(getattr(getattr(self, key_list[0]), key_list[1]),
                                key_list[2], value)

                else:
                    setattr(self, key, value)


class EDI_to_XML(object):
    """
    convert an EDI file to XML format
    
    """
    
    def __init__(self, **kwargs):
        
        self.edi_fn = None
        self.xml_fn = None
        self.cfg_fn = None
        
        self.parent_element = None
        
        self.mt_obj = None
        self.cfg_obj = XML_Config()
        
        self._order_list = ['Description',
                            'ProductID',
                            'SubType',
                            'Notes',
                            'Tags',
                            'ExternalURL',
                            'TimeSeriesArchived',
                            'Image',
                            'Original',
                            'Attachment',
                            'Provenance',
                            'Copyright',
                            'Site',
                            'FieldNotes',
                            'ProcessingInfo',
                            'StatisticalEstimates',
                            'DataTypes',
                            'InputChannels',
                            'OutputChannels',
                            'Data']
        
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            

        
    def read_edi(self, edi_fn=None):
        if edi_fn is not None:
            self.edi_fn = edi_fn
            
        self.mt_obj = mt.MT(self.edi_fn)
        
    def read_cfg(self, cfg_fn=None):
        if cfg_fn is not None:
            self.cfg_fn = cfg_fn
            
        self.cfg_obj = XML_Config()
        self.cfg_obj.read_cfg_file(self.cfg_fn)
        
    def _get_name(self, name):
        if name.find('(') > 0:
            l = name.split('(')
            name = l[0]
            meta_dict = {}
            for ll in l[1:]:
                ll = ll.split('=')
                meta_dict[ll[0]] = ll[1].replace(')', '')
        else:
            meta_dict = {}
        
        return name, meta_dict
        
    def make_element(self, parent, name):
        name, meta_dict = self._get_name(name)
        
        return ET.SubElement(parent, name, meta_dict)
        
    def write_element(self, parent_et, info_dict):
        
        for key in sorted(info_dict.keys()):
            if key == '_name':
                pass
            else:
                key_name, meta_dict = self._get_name(key)
                    
                k = ET.SubElement(parent_et, key_name, meta_dict)
                k.text = info_dict[key]
    
    def get_info(self, cfg_fn=None, edi_fn=None):
        """
        get information from config file and edi file
        """
        
        if cfg_fn is not None:
            self.cfg_fn = cfg_fn
        if edi_fn is not None:
            self.edi_fn = edi_fn
            
        self.read_edi()
        self.read_cfg()
        
        # --> extract information from EDI files
        # Site information
        self.cfg_obj.Site = Dummy()
        self.cfg_obj.Site._name = 'Site'
        self.cfg_obj.Site.Project = self.cfg_obj.Project
        self.cfg_obj.Site.Survey = self.cfg_obj.Survey
        self.cfg_obj.Site.DateCollected = self.mt_obj.edi_object.Header.acqdate
        self.cfg_obj.Site.Id = self.mt_obj.station
        self.cfg_obj.Site.AcquiredBy = self.mt_obj.edi_object.Header.acqby
        self.cfg_obj.Site.Start = self.mt_obj.edi_object.Header.acqdate
        self.cfg_obj.Site.End = self.mt_obj.edi_object.Header.acqdate
        self.cfg_obj.Site.RunList = '1'
        self.cfg_obj.Site.DataQualityNotes = self.cfg_obj.DataQualityNotes
        self.cfg_obj.Site.DataQualityWarnings = self.cfg_obj.DataQualityWarnings
        self.cfg_obj.Site.Location = Dummy(**{'Latitude':'{0:.6f}'.format(self.mt_obj.lat),
                                              'Longitude':'{0:.6f}'.format(self.mt_obj.lon),
                                              'Elevation(units=meters)':'{0:.3f}'.format(self.mt_obj.elev),
                                              'Declination(epoch=1995)':self.cfg_obj.Declination,
                                              '_name':'Location(datum={0})'.format(self.cfg_obj.Datum)})
        
        
        # Field Notes
        self.cfg_obj.FieldNotes = Dummy()
        self.cfg_obj.FieldNotes._name = 'FieldNotes(run=1)'
        self.cfg_obj.FieldNotes.Instrument = self.cfg_obj.Instrument
        self.cfg_obj.FieldNotes.Electrode = self.cfg_obj.Electrode
        self.cfg_obj.FieldNotes.Magnetometer = self.cfg_obj.Magnetometer
        #TODO: need to fill in more information on dipoles and magnetometers        
        
        # Input Channels
        self.cfg_obj.InputChannels = Dummy()
        self.cfg_obj.InputChannels._name = 'InputChannels(units=m)(ref=site)'

        self.cfg_obj.InputChannels.magnetic_hx = Dummy()
        hx = '(name=hx)(z=0)(y={0:.1f})(x={1:.1f})(orientation={2:.1f})'.format(
              self.mt_obj.edi_object.Define_measurement.meas_hx.y,
              self.mt_obj.edi_object.Define_measurement.meas_hx.x,
              self.mt_obj.edi_object.Define_measurement.meas_hx.azm)
        self.cfg_obj.InputChannels.magnetic_hx._name = 'Magnetic'+hx 
        
        self.cfg_obj.InputChannels.magnetic_hy = Dummy()
        hy = '(name=hy)(z=0)(y={0:.1f})(x={1:.1f})(orientation={2:.1f})'.format(
              self.mt_obj.edi_object.Define_measurement.meas_hy.y,
              self.mt_obj.edi_object.Define_measurement.meas_hy.x,
              self.mt_obj.edi_object.Define_measurement.meas_hy.azm)
        self.cfg_obj.InputChannels.magnetic_hy._name = 'Magnetic'+hy
        
        # Output Channels
        self.cfg_obj.OutputChannels = Dummy()
        self.cfg_obj.OutputChannels._name = 'OutputChannels(units=m)(ref=site)'
        try:
            hz = '(name=hz)(z=0)(y={0:.1f})(x={1:.1f})(orientation={2:.1f})'.format(
                  self.mt_obj.edi_object.Define_measurement.meas_hz.y,
                  self.mt_obj.edi_object.Define_measurement.meas_hz.x,
                  self.mt_obj.edi_object.Define_measurement.meas_hz.azm)
            self.cfg_obj.OutputChannels.magnetic_hz = Dummy()
            self.cfg_obj.OutputChannels.magnetic_hz._name = 'Magnetic'+hz 
        except AttributeError:
            print 'No HZ Information'
            
        ex = '(name=ex)(z=0)(y={0:.1f})(x={1:.1f})(y2={2:.1f})(x2={3:.1f})'.format(
                  self.mt_obj.edi_object.Define_measurement.meas_ex.y,
                  self.mt_obj.edi_object.Define_measurement.meas_ex.x,
                  self.mt_obj.edi_object.Define_measurement.meas_ex.y2,
                  self.mt_obj.edi_object.Define_measurement.meas_ex.x2)
        self.cfg_obj.OutputChannels.electric_ex = Dummy()
        self.cfg_obj.OutputChannels.electric_ex._name = 'Electric'+ex
            
        ey = '(name=ex)(z=0)(y={0:.1f})(x={1:.1f})(y2={2:.1f})(x2={3:.1f})'.format(
                  self.mt_obj.edi_object.Define_measurement.meas_ey.y,
                  self.mt_obj.edi_object.Define_measurement.meas_ey.x,
                  self.mt_obj.edi_object.Define_measurement.meas_ey.y2,
                  self.mt_obj.edi_object.Define_measurement.meas_ey.x2)
        self.cfg_obj.OutputChannels.electric_ey = Dummy()
        self.cfg_obj.OutputChannels.electric_ey._name = 'Electric'+ey
            
        self.format_data()
        
    def format_data(self):
        nf = self.mt_obj.Z.freq.size
        z_header = 'Z(units=[mV/km]/[nT])(type=complex)(size=2 2)'
        
        self.cfg_obj.Data = Dummy(**{'_name':'Data(count={0})'.format(nf)})        
        for ii in range(nf):
            p_name = 'Period_{0:02}'.format(ii)
            setattr(self.cfg_obj.Data, 
                    p_name, 
                    Dummy(**{'_name':'Period(units=sec)(value={0:.6g})'.format(self.mt_obj.Z.freq[ii])}))
            
#            for kk in range(2):
#                for jj in range(2):
                    
            setattr(getattr(self.cfg_obj.Data, p_name), 
                    z_header,
                    'ballz')
            
            
        
        
    def write_xml(self, edi_fn=None, xml_fn=None, cfg_fn=None):
        """
        write xml from edi
        """
        if edi_fn is not None:
            self.edi_fn = edi_fn
        if xml_fn is not None:
            self.xml_fn = xml_fn
        if edi_fn is not None:
            self.cfg_fn = cfg_fn
        
        if self.xml_fn is None:
            self.xml_fn = '{0}.xml'.format(self.edi_fn[0:-4])
        
        self.get_info()

        # make the top of the tree element        
        emtf = ET.Element('EM_TF')
        
        # loop over the important information sections
        for element in self._order_list:
            # get the information for the given element
            value = getattr(self.cfg_obj, element)
            
            # check if it is just a value
            if type(value) in [float, int, str]:
                self.write_element(emtf, {element:value})
                
            # if its a class Dummy, then check for single values or another
            # class Dummy
            elif isinstance(value, Dummy):
                print value._name
                # make a new tree limb
                new_element = self.make_element(emtf, value._name)
                
                # loop over attributes within the Dummy class, skipping _name
                for attr in sorted(value.__dict__.keys()):
                    if '_name' in attr:
                        pass
                    else:
                        new_value = getattr(value, attr)
                        if isinstance(new_value, Dummy):
                            # make a new tree limb
                            newer_element = self.make_element(new_element, 
                                                              new_value._name)
                            
                            # loop over attributes within the Dummy class, skipping _name
                            for new_attr in sorted(new_value.__dict__.keys()):
                                if '_name' in attr:
                                    pass
                                else:
                                    newer_value = getattr(new_value, new_attr)
                                    if isinstance(new_value, Dummy):
                                        newest_element = self.make_element(newer_element, 
                                                                           newer_value._name)
                                                                          
                                        self.write_element(newest_element, 
                                                           newer_value.__dict__)
                                    elif type(new_value) in [float, int, str]:
                                        self.write_element(newer_element, {new_attr:newer_value})
#                            newer_element = self.make_element(new_element, 
#                                                              new_value._name)
#                                                              
#                            newest_value = get_attr()
#                            self.write_element(newer_element, 
#                                               new_value.__dict__)
                        elif type(new_value) in [float, int, str]:
                            self.write_element(new_element, {attr:new_value})
            
            # write out estimates
            elif type(value) in [list, tuple]:
                new_element = self.make_element(emtf, element)
                for element_ii in value:
                    newer_element = self.make_element(new_element, 
                                                      element_ii._name)
                    self.write_element(newer_element, element_ii.__dict__)
  
        #--> write xml file
        with open(self.xml_fn, 'w') as fid:
            fid.write(ET.tostring(emtf))
        
        print '-'*50
        print '    Wrote xml file to: {0}'.format(self.xml_fn)
        print '-'*50
        # make a nice print out
        reparsed = minidom.parseString(ET.tostring(emtf, 'utf-8'))
        print(reparsed.toprettyxml(indent='    '))  
        
#==============================================================================
# Do the dirty work
#==============================================================================
test = EDI_to_XML()
test.edi_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\EDI_Files_birrp_mshs\Rotated_m18_deg\ms11.edi"
test.cfg_fn = r"C:\Users\jpeacock\Documents\PyScripts\xml_cfg_test.cfg"
test.write_xml()

cfg_test = XML_Config()
cfg_test.read_cfg_file(cfg_fn)

print isinstance(cfg_test.Provenance, Dummy)

    

      