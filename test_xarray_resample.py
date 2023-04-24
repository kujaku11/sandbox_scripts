# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 16:03:58 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
import xarray as xr
import pandas as pd
from scipy import signal
from mth5.timeseries import scipy_filters as spf

from matplotlib import pyplot as plt

# =============================================================================

n_samples = 4096
t = np.arange(n_samples)
data = np.sum(
    [
        np.cos(2 * np.pi * w * t + phi)
        for w, phi in zip(np.logspace(-3, 3, 20), np.random.rand(20))
    ],
    axis=0,
)

sample_rate = 64
new_sample_rate = "{0:.0f}N".format(1e9 / 1)

dt_index = pd.date_range(
    start="2020-01-01T00:00:00",
    end="2020-01-01T00:01:03.984375",
    periods=n_samples,
)

d = xr.DataArray(data, coords={"time": dt_index}, name="ex")
df = np.fft.rfft(d)
f = np.fft.rfftfreq(n_samples, 1 / sample_rate)
f_dec = np.fft.rfftfreq(int(n_samples / sample_rate), 1)

# resample with mean
d_mean = d.resample(time=new_sample_rate).mean()
df_mean = np.fft.rfft(d_mean)

# resample with median
d_median = d.resample(time=new_sample_rate).mean()
df_median = np.fft.rfft(d_median)

# decimate with scipy.signal.decimate
d_dec = signal.decimate(data, sample_rate)
df_dec = np.fft.rfft(d_dec)

# decimated with scipy wrapper for xarray
d_dec_sp = d.filt.decimate(1, dim="time")
df_dec_sp = np.fft.rfft(d_dec_sp)

# decimated with scipy wrapper for xarray
d_dec_sp2 = d.filt.decimate(8, dim="time").filt.decimate(1, dim="time")
df_dec_sp2 = np.fft.rfft(d_dec_sp2)


fig = plt.figure(1)
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2)

(l1,) = d.plot(ax=ax1, color="#1f77b4")
(l2,) = d_mean.plot(ax=ax1, color=(0.75, 0.75, 0))
(l3,) = d_median.plot(ax=ax1, color=(0.5, 0.75, 0.2))
(l4,) = ax1.plot(d_mean.time, d_dec, lw=2, color=(1, 0, 0))
(l5,) = ax1.plot(d_mean.time, d_dec_sp, lw=2, color=(0, 0, 1))
(l6,) = ax1.plot(d_mean.time, d_dec_sp2, lw=2, color=(0, 1, 1))

ax1.legend(
    [l1, l2, l3, l4, l5, l6],
    ["original", "mean", "median", "decimated", "xr_wrapper", "multiple_dec"],
)

ax2.loglog(f, np.abs(df) ** 2, color="#1f77b4")
ax2.loglog(f_dec, np.abs(df_mean) ** 2, color=(0.75, 0.75, 0))
ax2.loglog(f_dec, np.abs(df_median) ** 2, color=(0.5, 0.75, 0.2))
ax2.loglog(f_dec, np.abs(df_dec) ** 2, color=(1, 0, 0))
ax2.loglog(f_dec, np.abs(df_dec_sp) ** 2, color=(0, 0, 1))
ax2.loglog(f_dec, np.abs(df_dec_sp2) ** 2, color=(0, 1, 1))

plt.show()
