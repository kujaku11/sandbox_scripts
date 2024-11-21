# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 09:20:44 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import warnings
from pathlib import Path
from loguru import logger
import pandas as pd

from mtpy.processing import AuroraProcessing

warnings.filterwarnings("ignore")
# =============================================================================


survey_dir = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\mt\mt_short_course\data\mth5"
)

edi_path = survey_dir.parent.joinpath("EDI_Files_aurora")
edi_path.mkdir(exist_ok=True)

# Or try the alternative band file
band_file = (
    Path()
    .cwd()
    .parent.parent.joinpath("data", "transfer_functions", "bs_eight_level.cfg")
)
band_file_24k = Path(
    r"C:\Users\jpeacock\OneDrive - DOI\Documents\GitHub\iris-mt-course-2022\data\transfer_functions\phx_24k_bs.txt"
)

# this is how the different transfer functions will be merged.
merge_dict = {
    150: {"period_min": 1.0 / 30, "period_max": 10000},
    24000: {"period_min": 1.0 / 8000, "period_max": 1.0 / 31},
}

ap = AuroraProcessing(merge_dictionary=merge_dict)

ap.local_mth5_path = survey_dir.joinpath("phx_9043.h5")
ap.remote_mth5_path = survey_dir.joinpath("phx_1003.h5")

ap.local_station_id = "9043"
ap.remote_station_id = "1003"

ap.run_summary = ap.get_run_summary()

ap._remote_station_id = None
kds_24k = ap.create_kernel_dataset(
    local_station_id="9043", remote_station_id=None, sample_rate=24000
)

config_24k = ap.create_config(
    kds_24k, emtf_band_file=band_file_24k, num_samples_window=1024
)
config_24k.channel_nomenclature.ex = "e1"
config_24k.channel_nomenclature.ey = "e2"
config_24k.channel_nomenclature.hx = "h1"
config_24k.channel_nomenclature.hy = "h2"
config_24k.channel_nomenclature.hz = "h3"

for decimation in config_24k.decimations:
    # because we are only using a local station need to use the RME estimator.
    decimation.estimator.engine = "RME"
    decimation.window.type = "dpss"
    decimation.window.additional_args = {"alpha": 2.5}
    decimation.output_channels = ["e1", "e2", "h3"]
    decimation.input_channels = ["h1", "h2"]
    decimation.reference_channels = ["h1", "h2"]

    # here is where you would change windowing parameters
    decimation.window.overlap = 512
    decimation.window.num_samples = 1024
