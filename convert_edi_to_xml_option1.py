# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:41:03 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mtpy import MT

# =============================================================================
edi_file = Path(r"c:\Users\jpeacock\OneDrive - DOI\mt\Mines\CO701.edi")

mt_obj = MT()
mt_obj.read(edi_file)

# xml_obj = mt_obj.to_emtfxml()
