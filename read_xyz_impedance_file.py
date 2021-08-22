# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 17:23:12 2020

@author: jpeacock
"""


import pandas as pd

from pathlib import Path
from mtpy.core import mt

# =============================================================================
# Inputs
# =============================================================================
xyz_fn = Path(r"C:\Users\jpeacock\Downloads\Aug.25.xyz")

# read in file as a Pandas DataFrame
df = pd.read_csv(xyz_fn, delim_whitespace=True)

f_list = list(set([header.split("_")[1] for header in df.columns[14:]]))

z_dict = {}
for row in df.itertuples():
    entry = {}
