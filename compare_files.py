# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 14:24:14 2022

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path

# =============================================================================

ts_path = Path(r"c:\Users\jpeacock\Documents\GitHub\mt_metadata\mt_metadata\timeseries\standards")
tf_path = Path(r"c:\Users\jpeacock\Documents\GitHub\mt_metadata\mt_metadata\transfer_functions\tf\standards")

for ts_fn in ts_path.glob("*.json"):
    tf_fn = tf_path.joinpath(ts_fn.name)
    if tf_fn.exists():
        ts_lines = ts_fn.read_text()
        tf_lines = tf_fn.read_text()
        
        print('-'*25)
        print(f"File: {ts_fn.name}")
        with open(ts_fn, 'r') as file1:
            with open(tf_fn, 'r') as file2:
                difference = set(file1).difference(file2)
        
        difference.discard('\n')
        if len(difference) > 0:
            for line in difference:
                print(f"\t{line}")
        else:
            print("!!! All Good !!!")
                
        
        
