# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 18:02:53 2017

@author: jpeacock
"""

import xml.etree.cElementTree as ET
import mtpy.core.mt_xml as mtxml

# class Dummy(object):
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
        for ii in range(1, 10):
            new_attr_name = "{0}_{1:02}".format(attr_name, ii)
            if not hasattr(parent, new_attr_name):
                break

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
                parent_01 = getattr(child, attr_name)
                for child_01 in children_01:
                    attr_01_name = get_attr_name(parent_01, child_01.tag)

                    setattr(parent_01, attr_01_name, get_info_from_element(child_01))

                    children_02 = child_01.getchildren()
                    if len(children_02) > 0:
                        parent_02 = getattr(parent_01, attr_01_name)
                        for child_02 in children_02:
                            attr_02_name = get_attr_name(parent_02, child_02.tag)

                            setattr(
                                parent_02, attr_02_name, get_info_from_element(child_02)
                            )

                            children_03 = child_02.getchildren()
                            if len(children_03) > 0:
                                parent_03 = getattr(parent_02, attr_02_name)
                                for child_03 in children_03:
                                    attr_03_name = get_attr_name(
                                        parent_03, child_03.tag
                                    )

                                    setattr(
                                        parent_03,
                                        attr_03_name,
                                        get_info_from_element(child_03),
                                    )

    return child


k = mtxml.Dummy()
root = et_xml.getroot()
for element_00 in root.getchildren():
    setattr(k, element_00.tag, read_element(element_00))


# ext_url = et_xml.find('ProcessingInfo')
# k = read_element(ext_url)
