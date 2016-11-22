# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 18:35:05 2016

@author: jpeacock
"""

import mtpy.modeling.occam1d as occam1d

fn = r"c:\Users\jpeacock\Documents\SaudiArabia\edi_files_fixed_lon\101_rr.edi"

od = occam1d.Data()
od.write_data_file(edi_file=fn)
