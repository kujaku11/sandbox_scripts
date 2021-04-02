# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 11:44:42 2020

@author: jpeacock
"""

import re


fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\jvgr\submission_files\get_citations_from.tex"

with open(fn, "r") as fid:
    fn_str = fid.read()

try:
    found = re.search("cite{.+?}", fn_str)
except AttributeError:
    found = ""  # apply your error handling
