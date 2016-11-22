# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 17:20:17 2016

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\edi_files_fixed_lon"

edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi') and edi.find('only') == -1]
            

md = modem.Data(edi_list=edi_list)
md.period_min = .01
md.period_max = 3000.
md.max_num_periods = 24
md.write_data_file(save_path=r"c:\Users\jpeacock\Documents\SaudiArabia")

