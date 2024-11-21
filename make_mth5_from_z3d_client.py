# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 14:45:04 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from mth5.clients import MakeMTH5
# =============================================================================

m = MakeMTH5()
m.from_zen(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\ST2024\st2027", 
    calibration_path=r"c:\Users\jpeacock\OneDrive - DOI\MTData\antenna_20190411.cal",
    survey_id="mist")