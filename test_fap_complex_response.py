# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 11:16:55 2022

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
from mth5.io.zen import Z3D

# =============================================================================
z1 = Z3D(
    r"c:\Users\jpeacock\OneDrive - DOI\mt\cl2022\cl471\cl471_20221101_230517_256_EX.Z3D"
)
z1.read_z3d()

cr = z1.channel_response.complex_response(np.logspace(-3, 3, 10))
