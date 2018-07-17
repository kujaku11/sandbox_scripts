# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 10:17:28 2018

@author: jpeacock
"""

import subprocess
import os

dir_path = r"c:\Users\jpeacock\Documents\ClearLake\Figures"

for fn in [os.path.join(dir_path, ff) for ff in os.listdir(dir_path) if ff.endswith('.pdf')]:
    if os.path.getctime(fn) > 1530000000.0:
        std_out = subprocess.check_call(['magick',
                                         '-density','300',
                                         fn,
                                         '-flatten',
                                         fn[:-4]+'.jpg'])
        print std_out, fn[:-4]+'.jpg'