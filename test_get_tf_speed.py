# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 14:45:36 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from mth5.mth5 import MTH5
from mth5.groups import TransferFunctionGroup

# =============================================================================
m = MTH5()
m.open_mth5(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Battle_Mountain\EDI_files_birrp\edited\GeographicNorth\bm_collection.h5"
)

tf = m.get_transfer_function("bm24", "bm24", "unknown_survey")
