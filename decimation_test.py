# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 17:42:02 2021

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt

from mtpy.core import ts

df = 256
n = 3600 * df
dt = np.arange(n) / df

ex = np.zeros(n)
for p, a, s in zip(
    np.logspace(-3, 3, 50), np.random.randint(0, 20, 50), np.random.randn(50)
):
    ex += a * np.cos(np.pi * 2 * p * dt + p / np.pi)


t = ts.MTTS()

t.ts = ex
t.sampling_rate = df
t.start_time_utc = "2021-01-01T12:00:00"

plt.plot(t.ts)

t.decimate(256 / 4)
plt.plot(t.ts)
