# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 13:17:37 2019

@author: jpeacock
"""

import os
import shutil

cp_path = r"d:\Peacock\MTData\EDI_Files"

for dir_path in [r"c:\Users\jpeacock", r"d:\Peacock\MTData"]:
    for local_path, local_names, local_fn in os.walk(dir_path):
        for fn in local_fn:
            if fn.lower().endswith(".edi"):
                if os.path.exists(os.path.join(cp_path, fn)):
                    local_stat = os.stat(os.path.join(local_path, fn))
                    cp_stat = os.stat(os.path.join(cp_path, fn))

                    if local_stat.st_mtime > cp_stat.st_mtime:
                        shutil.copy(
                            os.path.join(local_path, fn), os.path.join(cp_path, fn)
                        )
                    else:
                        continue
                else:
                    shutil.copy(os.path.join(local_path, fn), os.path.join(cp_path, fn))
