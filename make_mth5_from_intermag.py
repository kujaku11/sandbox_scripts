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
        "observatory": obs,
        "type": ["adjusted"],
        "elements": [["x", "y"]],
        "sampling_period": [1],
        "start": ["2026-06-18T00:00:00"],
        "end": ["2026-06-24T13:00:00"],
    }
)


mth5_object = MakeMTH5.from_intermag(
    request_df,
    **{
        "save_path": r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2026\mth5",
        "interact": False,
        "mth5_version": "0.2.0",
    }
)
