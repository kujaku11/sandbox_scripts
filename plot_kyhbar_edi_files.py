# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 09:44:31 2018

@author: jpeacock
"""

import os
import mtpy.core.mt as mt

import mtpy.imaging.mtplot as mtplot
import mtpy

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\Kyhbar_EDI_Files"
edi_list = [os.path.join(edi_path, edi_fn) for edi_fn in os.listdir(edi_path)
            if edi_fn.endswith('.edi')]

#for edi_fn in edi_list:
#    mt_obj = mt.MT(edi_fn)

ptm = mtplot.plot_pt_map(fn_list=edi_list)