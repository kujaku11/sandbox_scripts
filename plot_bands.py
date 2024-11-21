# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 09:26:33 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from aurora.sandbox.io_helpers.emtf_band_setup import EMTFBandSetupFile
import numpy as np


from matplotlib import pyplot as plt
# =============================================================================
bs_fn = band_file_24k = Path(
    r"C:\Users\jpeacock\OneDrive - DOI\Documents\GitHub\iris-mt-course-2022\data\transfer_functions\phx_24k_bs.txt"
)

sample_rate = 24000
window_size = 1024
decimations = 2
decimation_factor = 4

a = EMTFBandSetupFile(filepath=bs_fn, sample_rate=24000)
band_edges = a.compute_band_edges([1, 4], [1024, 1024])

fig = plt.figure(1)

for dec_level, bands in band_edges.items():
    d_sample_rate = sample_rate / (1 + dec_level)
    plot_freq = np.linspace(0, d_sample_rate/2, num=window_size/2)
    ax = fig.add_subplot(len(band_edges.keys()), 1, dec_level+1)
    ax.stem(plot_freq, np.ones_like(plot_freq))
    for band in bands:
        ax.fill_betweenx([1, 1], band[0]], [1, ])
