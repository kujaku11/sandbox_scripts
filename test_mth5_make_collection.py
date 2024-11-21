# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 16:09:15 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mtpy import MTCollection

# =============================================================================
edi_dir = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\Documents\GitHub\iris-mt-course-2022\data\transfer_functions\earthscope"
)
tf_list = list(edi_dir.glob("*.xml"))
with MTCollection() as mc:
    mc.open_collection(r"c:\users\jpeacock\test_03.h5", libver="latest")
    mc.add_tf(tf_list)
    # sg = mc.mth5_collection.get_survey("Transportable_Array")
    # sg._has_read_metadata = True
    # sg.update_metadata()
