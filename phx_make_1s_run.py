# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 16:37:13 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from mth5.mth5 import MTH5

# =============================================================================


# with MTH5() as m:
m = MTH5()
m.open_mth5(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\Kilauea2023\phx\321_Phx\kl321_mth5_from_phoenix.h5"
)
run_group = m.get_run("321", "sr150_0001", "KLA")
rts = run_group.to_runts()
run_1s_ts = rts.resample_poly(1)
run_1s_ts.run_metadata.id = "sr1_0001"
new_run = m.add_run("321", "sr1_001", survey="KLA")
new_run.from_runts(run_1s_ts)
m.close_mth5()
