# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 14:37:02 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================

# =============================================================================
from mtpy import MTData

d1 = MTData()
d1.from_modem_data(
    r"c:\Users\jpeacock\OneDrive - DOI\Geysers\CEC\modem_inv\larger_grid_2023\gz_2023_modem_data_z03_tec_big_02.dat"
)
