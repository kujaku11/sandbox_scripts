# -*- coding: utf-8 -*-
"""
Created on Thu May 30 09:50:25 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import pandas as pd

from mth5.clients import MakeMTH5

# =============================================================================
obs = ["bou"]
n = len(obs)
request_df = pd.DataFrame(
    {
        "observatory": ["bou"],
        "type": ["adjusted"] * n,
        "elements": [["x", "y"]] * n,
        "sampling_period": [1] * n,
        "start": ["2024-06-22T12:00:00"],
        "end": [
            "2024-06-27T00:00:00",
        ],
    }
)

make_mth5_object = MakeMTH5(
    mth5_version="0.2.0",
    interact=False,
    save_path=r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2024",
)
mth5_object = make_mth5_object.from_usgs_geomag(request_df)
