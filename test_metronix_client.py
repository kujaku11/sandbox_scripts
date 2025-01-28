# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 09:22:15 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mth5.io.metronix import MetronixCollection, ATSS
from mth5.clients.metronix import MetronixClient
from mth5.clients import MakeMTH5

# =============================================================================

# a = ATSS(
#     fn=r"c:\Users\jpeacock\OneDrive - DOI\mt\metronix\mth5_files\small_example\Northern_Mining\stations\Sarıçam\run_001\084_ADU-07e_C002_THx_128Hz.atss")
# cr = a.header.get_channel_response()
# c = MetronixCollection(r"c:\Users\jpeacock\OneDrive - DOI\mt\metronix\mth5_files\small_example\Northern_Mining")
# #df = c.to_dataframe(run_name_zeros=2)
# r = c.get_runs([128, 2048, 1./2, 1./8], run_name_zeros=2)

# a = MetronixClient(r"c:\Users\jpeacock\OneDrive - DOI\mt\metronix\mth5_files\small_example\Northern_Mining", sample_rates=[128, 2048, 2])
# m = a.make_mth5_from_metronix()

m = MakeMTH5.from_metronix(
    r"c:\Users\jpeacock\OneDrive - DOI\mt\metronix\mth5_files\small_example\Northern_Mining",
    sample_rates=[128, 2048, 1.0 / 2, 1.0 / 8],
    mth5_filename="from_metronix_test_s.h5",
    run_name_zeros=0,
)

from mtpy.processing import AuroraProcessing

ap = AuroraProcessing()
ap.local_station_id = "Sarıçam"
ap.local_mth5_path = r"c:\Users\jpeacock\OneDrive - DOI\mt\metronix\mth5_files\small_example\Northern_Mining\from_metronix_test_s.h5"

p = ap.process(sample_rates=[128])  # , 2048, 1.0 / 2, 1.0 / 8])
