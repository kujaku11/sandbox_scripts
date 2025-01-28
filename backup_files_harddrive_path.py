# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 10:08:47 2015

@author: jpeacock
"""
# ==============================================================================
# Imports
# ==============================================================================
from pathlib import Path
import shutil

import os
import time


# ==============================================================================
# Helper functions
# ==============================================================================
def copy_file(original_file, save_path):
    save_file = save_path.joinpath(original_file.name)
    if save_file.exists():
        if original_file.stat().st_mtime == save_file.stat().st_mtime:
            return
        shutil.copy(original_file, save_file)
    else:
        shutil.copy(original_file, save_file)

# ==============================================================================
# Input variables
# ==============================================================================

# dirpath = r"/mnt/hgfs/jpeacock/Documents"
home_path = Path(r"C:\Users\jpeacock\OneDrive - DOI")
save_path = Path(r"E:\Peacock_Backup\OneDrive - DOI")


for fn in home_path.iterdir():
    if fn.is_file():
        copy_file(fn, save_path)
    else:
        
        




    

