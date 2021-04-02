# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 21:10:32 2019

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

dt = 1.0 / 80
train_type = "competitor"

if train_type == "cool":
    cmap = "Blues"
    # phase_dict = {'1':{'f':5, 't_on':10, 't_off':0, 'reps':12, 't_total':120, 'power':1},
    #              '2':{'f':25, 't_on':7, 't_off':4, 'reps':32, 't_total':224+128, 'power':1},
    #              '3':{'f':2, 't_on':5, 't_off':0, 'reps':9, 't_total':45, 'power':1},
    #              '4':{'f':25, 't_on':7, 't_off':4, 'reps':32, 't_total':224+128, 'power':1},
    #              '5':{'f':2, 't_on':5, 't_off':0, 'reps':9, 't_total':45, 'power':1},
    #              '6':{'f':40, 't_on':6, 't_off':5, 'reps':32, 't_total':192+160, 'power':1},
    #              '7':{'f':2, 't_on':5, 't_off':0, 'reps':9, 't_total':45, 'power':1},
    #              '8':{'f':40, 't_on':6, 't_off':5, 'reps':32, 't_total':192+160, 'power':1},
    #              '9':{'f':3, 't_on':10, 't_off':0, 'reps':12, 't_total':120, 'power':1}}

    phase_dict = {
        1: {"f": 5, "t_on": 10, "t_off": 0, "reps": 12, "t_total": 120, "power": 1},
        2: {
            "f": 30,
            "t_on": 6,
            "t_off": 5,
            "reps": 32,
            "t_total": 224 + 128,
            "power": 1,
        },
        3: {"f": 2, "t_on": 5, "t_off": 0, "reps": 9, "t_total": 45, "power": 1},
        4: {
            "f": 30,
            "t_on": 6,
            "t_off": 5,
            "reps": 32,
            "t_total": 224 + 128,
            "power": 1,
        },
        5: {"f": 2, "t_on": 5, "t_off": 0, "reps": 9, "t_total": 45, "power": 1},
        6: {
            "f": 40,
            "t_on": 6,
            "t_off": 5,
            "reps": 32,
            "t_total": 192 + 160,
            "power": 1,
        },
        7: {"f": 2, "t_on": 5, "t_off": 0, "reps": 9, "t_total": 45, "power": 1},
        8: {
            "f": 40,
            "t_on": 6,
            "t_off": 5,
            "reps": 32,
            "t_total": 192 + 160,
            "power": 1,
        },
        9: {"f": 3, "t_on": 10, "t_off": 0, "reps": 12, "t_total": 120, "power": 1},
    }
elif train_type == "competitor":
    cmap = "BuPu"
    phase_dict = {
        1: {"f": 5, "t_on": 6, "t_off": 6, "reps": 10, "t_total": 120, "power": 0.95},
        2: {
            "f": 31,
            "t_on": 2.81,
            "t_off": 2.95,
            "reps": 17,
            "t_total": 47.77 + 50.15,
            "power": 0.95,
        },
        3: {
            "f": 38,
            "t_on": 5.05,
            "t_off": 4.95,
            "reps": 8,
            "t_total": 40.4 + 39.6,
            "power": 0.95,
        },
        4: {"f": 5, "t_on": 6, "t_off": 6, "reps": 10, "t_total": 120, "power": 0.95},
        5: {
            "f": 31,
            "t_on": 2.81,
            "t_off": 2.95,
            "reps": 17,
            "t_total": 47.77 + 50.15,
            "power": 0.95,
        },
        6: {
            "f": 38,
            "t_on": 5.05,
            "t_off": 4.95,
            "reps": 8,
            "t_total": 40.4 + 39.6,
            "power": 0.95,
        },
        7: {"f": 5, "t_on": 6, "t_off": 6, "reps": 10, "t_total": 120, "power": 0.95},
        8: {
            "f": 31,
            "t_on": 2.81,
            "t_off": 2.95,
            "reps": 17,
            "t_total": 47.77 + 50.15,
            "power": 0.95,
        },
        9: {
            "f": 38,
            "t_on": 5.05,
            "t_off": 4.95,
            "reps": 8,
            "t_total": 40.4 + 39.6,
            "power": 0.95,
        },
        10: {"f": 5, "t_on": 6, "t_off": 6, "reps": 10, "t_total": 120, "power": 0.95},
        11: {
            "f": 31,
            "t_on": 2.81,
            "t_off": 2.95,
            "reps": 17,
            "t_total": 47.77 + 50.15,
            "power": 0.95,
        },
        12: {
            "f": 38,
            "t_on": 5.05,
            "t_off": 4.95,
            "reps": 8,
            "t_total": 40.4 + 39.6,
            "power": 0.95,
        },
        13: {"f": 5, "t_on": 6, "t_off": 6, "reps": 10, "t_total": 120, "power": 0.95},
        14: {
            "f": 31,
            "t_on": 2.81,
            "t_off": 2.95,
            "reps": 17,
            "t_total": 47.77 + 50.15,
            "power": 0.95,
        },
        15: {
            "f": 38,
            "t_on": 5.05,
            "t_off": 4.95,
            "reps": 8,
            "t_total": 40.4 + 39.6,
            "power": 0.95,
        },
        16: {"f": 5, "t_on": 6, "t_off": 6, "reps": 10, "t_total": 120, "power": 0.95},
        17: {
            "f": 31,
            "t_on": 2.81,
            "t_off": 2.95,
            "reps": 17,
            "t_total": 47.77 + 50.15,
            "power": 0.95,
        },
        18: {
            "f": 38,
            "t_on": 5.05,
            "t_off": 4.95,
            "reps": 8,
            "t_total": 40.4 + 39.6,
            "power": 0.95,
        },
    }


def phase(f, t_on, t_off, reps, power, dt=dt, **kwargs):
    """
    make a phase
    """

    df = 1.0 / dt
    n = (t_on + t_off) * reps
    p = np.zeros(int(n * df))
    t_on_arr = np.arange(t_on * df) * dt

    n_on = int(t_on * df)
    n_off = int(t_off * df)
    t_on_arr = np.arange(n_on) * dt
    for ii in range(reps):
        index_01 = int(ii * (n_on + n_off))
        index_02 = index_01 + n_on
        p[index_01:index_02] = power * np.cos(2 * np.pi * f * t_on_arr)
        if t_off != 0:
            index_03 = index_02
            index_04 = (ii + 1) * (n_on + n_off)
            p[index_03:index_04] = 0

    return p


n_total = sum([phase_dict[key]["t_total"] for key in phase_dict.keys()])
pulse_train = np.array([])
for ii, key in enumerate(sorted(phase_dict.keys())):
    p1 = phase(**phase_dict[key])
    pulse_train = np.append(pulse_train, p1)

# =============================================================================
# plot
# =============================================================================
t = np.arange(pulse_train.size) * dt
fig = plt.figure(1)
fig.clf()
gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
ax1 = fig.add_subplot(gs[0])
spec = ax1.specgram(
    pulse_train,
    pad_to=2 ** 6,
    NFFT=2 ** 6,
    noverlap=2 ** 4,
    Fs=1.0 / dt,
    cmap=cmap,
    mode="psd",
)
ax2 = fig.add_subplot(gs[1])
(l,) = ax2.plot(t, pulse_train, "k", lw=0.25)
ax2.set_xlim(t.min(), t.max())
plt.tight_layout()
plt.show()
