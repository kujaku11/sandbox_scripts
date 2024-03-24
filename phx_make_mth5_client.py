# -*- coding: utf-8 -*-
"""

Created on Fri Mar 22 21:43:12 2024

:author: Jared Peacock

:license: MIT

"""
# =============================================================================
# Imports
# =============================================================================

from pathlib import Path
from mth5.clients.phoenix import PhoenixClient

# =============================================================================

phx = PhoenixClient()

phx.sample_rates = [150, 24000]
phx.calibration_path = Path(r"c:\MT\ST2024\1014")
phx.data_path = Path(r"c:\MT\ST2024\1014\Data")

phx_mth5 = phx.make_mth5_from_phoenix()
