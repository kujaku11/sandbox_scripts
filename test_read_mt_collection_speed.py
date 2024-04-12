# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 15:49:05 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from mtpy import MTCollection

# =============================================================================

with MTCollection() as mc:
    mc.open_collection(
        r"c:\Users\jpeacock\OneDrive - DOI\Documents\GitHub\iris-mt-course-2022\data\transfer_functions\yellowstone_mt_collection_02.h5"
    )
    mc.apply_bbox(*[-111.4, -109.85, 44, 45.2])
    mt_data = mc.to_mt_data()
