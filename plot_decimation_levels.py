# -*- coding: utf-8 -*-
"""
Created on Wed May 24 14:27:12 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# =============================================================================

starting_sample_rate = 1
window_length = 128
decimation_factor = 4

band_path = r"c:\Users\jpeacock\OneDrive - DOI\Documents\GitHub\aurora\aurora\config\emtf_band_setup\bs_six_level.cfg"

df = pd.read_csv(
    band_path,
    skiprows=1,
    sep="\s+",
    names=["decimation_level", "lower_bound_index", "upper_bound_index"],
)

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

color_dict = {
    1: (181 / 255, 43 / 255, 43 / 255),
    2: (181 / 255, 43 / 255, 171 / 255),
    3: (61 / 255, 43 / 255, 181 / 255),
    4: (43 / 255, 135 / 255, 181 / 255),
    5: (43 / 255, 181 / 255, 116 / 255),
    6: (181 / 255, 149 / 255, 43 / 255),
    7: (181 / 255, 61 / 255, 43 / 255),
}

for row in df.itertuples():
    delta_f = (
        1.0 / (decimation_factor ** (row.decimation_level - 1))
    ) / window_length
    f = np.arange(window_length) * delta_f
    ax.semilogx(
        f[row.lower_bound_index - 1 : row.upper_bound_index],
        [row.decimation_level]
        * (row.upper_bound_index - row.lower_bound_index + 1),
        lw=3,
        color=color_dict[row.decimation_level],
    )
    y = [-1, row.decimation_level + 1]
    ax.fill_betweenx(
        y,
        [f[row.lower_bound_index - 1]] * 2,
        [f[row.upper_bound_index - 1]] * 2,
        color=color_dict[row.decimation_level],
        alpha=0.5,
    )
    ax.plot(
        [f[row.lower_bound_index - 1]] * 2,
        y,
        color=color_dict[row.decimation_level],
        lw=1,
    )
    ax.plot(
        [f[row.upper_bound_index - 1]] * 2,
        y,
        color=color_dict[row.decimation_level],
        lw=1,
    )
ax.grid(which="both")
ax.set_ylim((0, df.decimation_level.max() + 0.5))
plt.show()
