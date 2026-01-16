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
obs = ["frn"]
n = len(obs)
request_df = pd.DataFrame(
    {
        "observatory": obs,
        "type": ["adjusted"] * n,
        "elements": [["x", "y"]] * n,
        "sampling_period": [1] * n,
        "start": ["2025-08-22T00:00:00"] * n,
        "end": [
            "2025-08-30T00:00:00",
        ]
        * n,
    }
)


mth5_object = MakeMTH5.from_usgs_geomag(
    request_df,
    **{
        "save_path": r"c:\Users\jpeacock\OneDrive - DOI\MTData\CL2025\mth5",
        "interact": False,
        "mth5_version": "0.2.0",
    }
)
