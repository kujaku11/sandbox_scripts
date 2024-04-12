# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 16:09:45 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""

from mtpy import MT

fn = r"c:\Users\jpeacock\OneDrive - DOI\ClearLake\EDI_files_birrp\edited\cl141.edi"

m1 = MT()
m1.read(fn)

# m1.read(r"c:\Users\jpeacock\OneDrive - DOI\mt\IDL10bc_L11x.zrr")
