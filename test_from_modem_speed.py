# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 13:09:31 2024

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from mtpy import MTData
from mtpy.core import MTDataFrame

# =============================================================================
md = MTData()
md.from_modem(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\BuffaloValley\modem_inv\inv_02\bv_modem_data_z07_tls_tec_02.dat"
)
df = md.to_dataframe()
a = MTDataFrame(df)
