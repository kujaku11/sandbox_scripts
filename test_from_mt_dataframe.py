# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 12:56:43 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from mtpy.core.mt_data import MTData


# =============================================================================

d = MTData()
d.from_modem_data(
    r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GreatBasin\modem_inv\cv_inv_01\cv_z03_t02_c05_NLCG_010.res"
)

# d.from_modem_data(
#     r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Battle_Mountain\modem_inv\inv_04\bm_z03_t02_c04_136.dat",
#     file_type="model",
# )

# p = d.plot_mt_response(
#     station_key=["data.bm100", "model.bm100"],
#     plot_model_error="model_error",
#     plot_style="compare",
# )
