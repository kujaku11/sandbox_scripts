# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 18:02:53 2017

@author: jpeacock
"""

import xml.etree.cElementTree as ET
import mtpy.core.mt_xml as mtxml

#class Dummy(object):
#    def __init__(self, **kwargs):
#        for key in kwargs.keys():
#            setattr(self, key, kwargs[key])

def make_attr_str(child):
    tag = child.tag
    attributes = child.attrib
    for key in attributes.keys():
        tag += '({0}={1})'.format(key, attributes[key])
        
    return tag

xml_fn = r"C:\Users\jpeacock\Documents\PyScripts\ORL09bc_J9.xml"

et_xml = ET.parse(xml_fn)

root = et_xml.getroot()

e2xml = mtxml.EDI_to_XML()


for child_00 in root.getchildren():
    attr_00 = make_attr_str(child_00)
    
    if len(child_00.getchildren()) > 0:
        value_00 = mtxml.Dummy(**{'_name':attr_00})
        for child_01 in child_00.getchildren():
            attr_01 = make_attr_str(child_01)
            if len(child_01.getchildren()) > 0:
                value_01 = mtxml.Dummy()
                for child_02 in child_01.getchildren():
                    attr_02 = make_attr_str(child_02)
                    value_02 = child_02.text
                    setattr(value_01, attr_02, value_02)
                setattr(value_01, '_name', attr_01)

            else:
                value_01 = child_01.text
            setattr(value_00, attr_01, value_01)
        
        setattr(value_00, '_name', attr_00)
        
    else:
        value_00 = child_00.text
    if '(' and ')' in attr_00:
        setattr(e2xml.cfg_obj, child_00.tag, value_00)
    else:
        setattr(e2xml.cfg_obj, attr_00, value_00)
    
e2xml.write_xml(xml_fn=r"C:\Users\jpeacock\Documents\PyScripts\Test_read_xml.xml")
    
   

