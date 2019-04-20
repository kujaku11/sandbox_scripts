# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 14:39:53 2019

@author: jpeacock
"""

import os
import pandas as pd
import glob

edi_dirs = ['c:\Users\jpeacock', 'd:\Peacock\MTData']
fn_db = pd.DataFrame()
for edi_dir in edi_dirs:
    for root, dirs, fn_list in os.walk(edi_dir):
        for fn in fn_list:
            if glob.fnmatch(fn, '.edi'):
                fn_dict = {}
                fn_dict['fn'] = fn
                fn_dict['fn_path'] = os.path.join(root, fn)
                fn_dict['fn_date'] = os.path.getmtime(fn_dict['fn_path'])
                fn_db.append(pd.DataFrame(fn_dict))