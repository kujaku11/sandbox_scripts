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

def get_info_from_element(element):
    return_obj = mtxml.Dummy()
    return_obj._name = element.tag
    try:
        return_obj._text = element.text.strip()
    except AttributeError:
        return_obj._text = None
    return_obj._attr = element.attrib
    
    return return_obj
    
def get_attr_name(parent, attr_name):
    if hasattr(parent, attr_name):
        print 'parent already has attribute {0}'.format(attr_name)
        new_attr_name = '{0}_{1:02}'.format(attr_name, 1)
        if hasattr(parent, new_attr_name):
            count = 2
            while hasattr(parent, '{0}_{1:02}'.format(attr_name, count)):
                new_attr_name = '{0}_{1:02}'.format(attr_name, count)
                count += 1
    else:
        new_attr_name = attr_name
    
    return new_attr_name

xml_fn = r"C:\Users\jpeacock\Documents\PyScripts\ORL09bc_J9.xml"

e2xml = mtxml.EDI_to_XML()

et_xml = ET.parse(xml_fn)


def read_element(element):
    """
    read a given element and return something useful
    """
    
    child = get_info_from_element(element)
    
    children = element.getchildren()
    if len(children) > 0:
        for child_00 in children:
            attr_name = get_attr_name(child, child_00.tag)
            setattr(child, attr_name, get_info_from_element(child_00))
            
            children_01 = child_00.getchildren()
            if len(children_01) > 0:
                for child_01 in children_01:
                    attr_01_name = get_attr_name(getattr(child, attr_name),
                                                 child_01.tag)
                                                 
                    setattr(getattr(child, child_00.tag), attr_01_name,
                            get_info_from_element(child_01))
                    


                
            else:
                pass
                    

    else:
        pass
        
    return child

# read description
#description = et_xml.find('Description')
#k = read_element(description)

ext_url = et_xml.find('FieldNotes')
k = read_element(ext_url)


#root = et_xml.getroot()
#
#
#
#

#    
##e2xml.write_xml(xml_fn=r"C:\Users\jpeacock\Documents\PyScripts\Test_read_xml.xml")
#    
#   

