# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 08:22:27 2018

@author: jpeacock
"""
import mtpy.usgs.usgs_archive as archive
# =============================================================================
# Test
# =============================================================================
cfg_fn = r"C:\Users\jpeacock\Documents\imush\xml_config_test.txt"

m = archive.XMLMetadata()
m.read_config_file(cfg_fn)
m.write_xml_file(r"c:\Users\jpeacock\Documents\imush\test.xml")

m = archive.XMLMetadata()
m.read_config_file(cfg_fn)
m.survey.east = -121.34
m.survey.west = -121.34
m.survey.north = 38.75
m.survey.south = 38.75

m.title += ' station006'
m.supplement_info += 'file list: file1, file2, file3'
m.survey.begin_date = '20170101T10:30:10 UTC'
m.survey.end_date = '20170103T18:10:40 UTC'

m.write_xml_file("c:\Users\jpeacock\Documents\imush\station_test.xml",
                 write_station=True)