# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 18:54:12 2018

@author: jpeacock-pr
"""

import os
import mtpy.core.mt as mt

zmm_path = r"c:\MT\MB\zmmfiles"
zmm_list = [
    os.path.join(zmm_path, zmm) for zmm in os.listdir(zmm_path) if zmm.endswith(".zmm")
]

for zmm in zmm_list:
    mt_obj = mt.MT(zmm)
    mt_obj.write_mt_file()
