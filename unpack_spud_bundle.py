# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 10:24:20 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import shutil

# =============================================================================

bundle = Path(r"c:\Users\jpeacock\Downloads\SPUD_bundle_2024-01-03T18.40.14")
edi_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES")

for fn in bundle.rglob("*.edi"):
    new_path = edi_path.joinpath(fn.name)
    if not new_path.exists():
        shutil.copy(fn, new_path)
        print(f"Copied: {fn.name} to {new_path}")
