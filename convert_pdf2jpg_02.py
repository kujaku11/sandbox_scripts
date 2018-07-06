# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 10:17:28 2018

@author: jpeacock
"""

import subprocess
import os

dir_path = r"c:\Users\jpeacock\Documents\Geysers\Figures"

for fn in [os.path.join(dir_path, ff) for ff in os.listdir(dir_path) if ff.endswith('.pdf')]:
    
    std_out = subprocess.check_call(['magick',
                                     fn,
                                     '-density','300',
                                     '-flatten',
                                     fn[:-4]+'.jpg'])
    print std_out, fn[:-4+'.jpg']