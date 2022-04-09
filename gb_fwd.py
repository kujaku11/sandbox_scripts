# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 10:36:35 2022

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
from mtpy.modeling.modem import Model

# =============================================================================

res_levels = [
    (0, 2, 10),
    (2, 5, 30),
    (5, 25, 300),
    (25, 60, 50),
    (60, 150, 100),
    (150, 1000, 10),
]

m = Model()
m.read_model_file(
    r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\modem_inv\mnp_03\mnp_z03_t02_c02_098.rho"
)

fwd = np.zeros_like(m.res_model)

for r in res_levels:

    test = np.where((m.grid_z[:-1] >= r[0] * 1000) & (m.grid_z[:-1] < r[1] * 1000))
    fwd[:, :, test] = r[2]

# fwd[np.where(m.res_model <1)] = 0.3
m.write_model_file(model_fn_basename="mnp_fwd.rho", res_model=fwd)
