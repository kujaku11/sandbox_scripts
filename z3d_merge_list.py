# -*- coding: utf-8 -*-
"""
Created on Thu Feb 14 11:02:09 2019

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import os
import pandas as pd
from mtpy.usgs import zen

# =============================================================================
# Inputs
# =============================================================================
z3d_dir = r"c:\Users\jpeacock\Documents\imush\G016-5"
# =============================================================================
# File
# =============================================================================
fn_list = [
    os.path.join(z3d_dir, fn)
    for fn in os.listdir(z3d_dir)
    if fn.lower().endswith(".z3d")
]

merge_list = []

for fn in fn_list:
    z3d_obj = zen.Zen3D(fn=fn)
    z3d_obj.read_all_info()
    merge_list.append({"fn": fn, "start_date": z3d_obj.zen_schedule, "df": z3d_obj.df})

df = pd.DataFrame(merge_list)

start_list = list(set(df["start_date"]))

merge_fn_list = []
for start in start_list:
    merge_fn_list.append(df[df.start_date == start]["fn"].tolist())
