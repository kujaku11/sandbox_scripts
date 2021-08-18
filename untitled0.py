# -*- coding: utf-8 -*-
"""

Created on Tue Jun  1 12:28:28 2021

:author: Jared Peacock

:license: MIT

"""
from pykml import parser

kml_fn = r"c:\Users\peaco\Documents\FieldWork\ClearLake.kml"
with open(kml_fn, 'r') as fid:
    k = parser.parse(fid)