# -*- coding: utf-8 -*-
"""
Created on Wed May  4 14:42:08 2022

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from obspy import UTCDateTime
from aurora.sandbox.io_helpers.fdsn_dataset_config import FDSNDatasetConfig
from aurora.sandbox.io_helpers.make_mth5_helpers import create_from_server_multistation

# =============================================================================

# Jasper Ridge stanford
jrsc = FDSNDatasetConfig()
jrsc.dataset_id = "jrsc"
jrsc.network = "BK"
jrsc.station = "JRSC"
jrsc.starttime = UTCDateTime("2022-04-18T00:00:00.000000Z")
jrsc.endtime = UTCDateTime("2022-04-30T00:00:00.000000Z")
jrsc.channel_codes = "BT1,BT2"
jrsc.description = "Jasper Ridge Stanford, CA"
jrsc.components_list = ["hx", "hy"]


create_from_server_multistation(
    jrsc, source="NCEDC", target_folder=Path(r"c:\Users\jpeacock"),
)
