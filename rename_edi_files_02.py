# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 12:14:28 2021

@author: jpeacock
"""
from pathlib import Path
from mt_metadata.transfer_functions.io.edi import EDI

fg_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES")

fg_files = list(fg_path.glob("FRG*"))

for ii, fn in enumerate(fg_files, 100):
    e1 = EDI(fn)
    e1.station = f"frg{ii:03}"
    e1.write(fn)
    
    
