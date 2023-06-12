# -*- coding: utf-8 -*-
"""
Created on Thu Aug 04 18:02:56 2016

@author: jpeacock-pr
"""

from pathlib import Path
import shutil

# data_folder = r"d:\WD SmartWare.swstor\IGSWMBWGLTGG032\Volume.b5634234.da89.11e2.aa2b.806e6f6e6963\MT\SCEC"
# data_folder = "/mnt/hgfs/MT_Data/GB2022"
data_folder = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\GZ2023")
# data_folder = r"c:\MT\GB2022"
for folder in data_folder.iterdir():
    if folder.is_dir():
        for p_folder in folder.iterdir():
            if p_folder.is_dir():
                if p_folder.name in ["TS"]:
                    shutil.rmtree(p_folder)
                    print(f"Removed {p_folder}")
                try:
                    fp = int(p_folder.name)
                    shutil.rmtree(p_folder)
                    print(f"Removed {p_folder}")
                except ValueError:
                    continue
            else:
                if ".h5" in p_folder.suffix:
                    p_folder.unlink()
                    print(f"Removed {p_folder}")
