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

from mth5.clients import MakeMTH5

# =============================================================================

# phx = PhoenixClient(
#     r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_short_course\data\phx\remote",
#     mth5_filename="remote.h5",
# )

# phx.sample_rates = [150, 24000]
# phx.receiver_calibration_dict = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_short_course\data\phx\remote\calibrations"
# )
# phx.sensor_calibration_dict = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_short_course\data\phx\remote\calibrations"
# )

# phx_mth5 = phx.make_mth5_from_phoenix()


# maker = MakeMTH5
# phx_mth5_fn = MakeMTH5.from_phoenix(
#     r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_short_course\data\phx\remote",
#     mth5_filename="remote_02.h5",
#     sample_rates=[150],
#     receiver_calibration_dict=Path(
#         r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_short_course\data\phx\remote\calibrations"
#     ),
#     sensor_calibration_dict=Path(
#         r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_short_course\data\phx\remote\calibrations"
#     ),
# )

maker = MakeMTH5
phx_mth5_fn = MakeMTH5.from_phoenix(
    r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_short_course\data\phx\9043",
    mth5_filename="phx_9043.h5",
    sample_rates=[150, 24000],
    receiver_calibration_dict=Path(
        r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_short_course\data\phx\9043\calibrations"
    ),
    sensor_calibration_dict=Path(
        r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_short_course\data\phx\9043\calibrations"
    ),
)
