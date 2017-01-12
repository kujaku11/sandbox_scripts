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

#==============================================================================
# Useful Functions
#==============================================================================
    


class Edi_to_xml(object):
    """
    convert an EDI file to XML format
    
    """
    
    def __init__(self, **kwargs):
        
        self.edi_fn = None
        self.xml_fn = None
        self.cfg_fn = None
        
        self.parent_element = None
        
        self.mt_obj = None
        
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
                            'InputChannel',
                            'OutputChannel',
                            'DataCount']
        
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
            if line[0] == '#':
                pass
            elif line == '\n':
                pass
            else:
                line_list = line.strip().split('=')
                key = line_list[0].strip()
                value = line_list[1].strip()
                
                if key.find('.') > 0:
                    key_list = key.split('.')
                    if len(key_list) == 2:
                        try:
                            self.cfg_dict[key_list[0]][key_list[1]] = value
                        except KeyError:
                            self.cfg_dict[key_list[0]] = {key_list[1]:value}
                    elif len(key_list) == 3:
                        try: 
                            self.cfg_dict[key_list[0]][key_list[1]][key_list[2]] = value
                        except KeyError:
                            try:
                                self.cfg_dict[key_list[0]][key_list[1]] = {key_list[2]:value}
                            except KeyError:
                                self.cfg_dict[key_list[0]] = {key_list[1]:{key_list[2]:value}}
    
                else:
                    self.cfg_dict[key] = value
        self.cfg_dict
        
    def read_edi(self, edi_fn=None):
        if edi_fn is not None:
            self.edi_fn = edi_fn
            
        self.mt_obj = mt.MT(self.edi_fn)
        
    def write_element(self, parent_et, info_dict):
        
        for key in info_dict.keys():
            k = ET.SubElement(parent_et, key)
            k.text = info_dict[key]
        
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
        
        self.read_edi()
        self.read_cfg_file()
        
        emtf = ET.Element('EM_TF')
        for element in self._order_list[0:10]:
            try:
                params = self.cfg_dict[element]
                if type(params) is dict:
                    new_element = ET.SubElement(emtf, element)
                    print 'New Element {0}'.format(element)
                    for key in params.keys():
                        if type(params[key]) is dict:
                            print key, params[key]
                            newer_element = ET.SubElement(new_element, key)
                            self.write_element(newer_element, params[key])
                        else:
                            print params
                            self.write_element(new_element, params)
                    
                else:
                    self.write_element(emtf, {element:self.cfg_dict[element]})
            except KeyError:
                print 'Could not find information on {0}'.format(element)
            
        
        
        # make a nice print out
        reparsed = minidom.parseString(ET.tostring(emtf, 'utf-8'))
        print(reparsed.toprettyxml(indent='    '))  
        
#==============================================================================
# Do the dirty work
#==============================================================================
test = Edi_to_xml()
test.edi_fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\EDI_Files_birrp_mshs\Rotated_m18_deg\ms11.edi"
test.cfg_fn = r"C:\Users\jpeacock\Documents\PyScripts\xml_cfg_test.cfg"
test.write_xml()


    

      