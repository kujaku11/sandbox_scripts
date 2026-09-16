# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 13:17:37 2019

@author: jpeacock
"""

import os
import shutil
from pathlib import Path

base_dir = Path(r"c:\Users\jpeacock\OneDrive - DOI")
cp_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES")

for edi_fn in base_dir.rglob("*.edi"):
    if edi_fn.is_file():
        if cp_path.joinpath(edi_fn.name).exists():
            local_stat = edi_fn.stat()
            cp_stat = cp_path.joinpath(edi_fn.name).stat()

            if local_stat.st_mtime > cp_stat.st_mtime:
                shutil.copy(edi_fn, cp_path.joinpath(edi_fn.name))
            else:
                continue
        else:
            shutil.copy(edi_fn, cp_path.joinpath(edi_fn.name))

# for dir_path in [r"c:\Users\jpeacock\OneDrive - DOI"]:
#     for local_path, local_names, local_fn in os.walk(dir_path):
#         for fn in local_fn:
#             if fn.lower().endswith(".edi"):
#                 if os.path.exists(os.path.join(cp_path, fn)):
#                     local_stat = os.stat(os.path.join(local_path, fn))
#                     cp_stat = os.stat(os.path.join(cp_path, fn))

#                     if local_stat.st_mtime > cp_stat.st_mtime:
#                         shutil.copy(
#                             os.path.join(local_path, fn), os.path.join(cp_path, fn)
#                         )
#                     else:
#                         continue
#                 else:
#                     shutil.copy(os.path.join(local_path, fn), os.path.join(cp_path, fn))
