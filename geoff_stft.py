# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 12:59:06 2022

@author: jpeacock
"""

import pandas as pd
from mtpy.imaging.plotspectrogram import PlotTF


fn = r"c:\Users\jpeacock\Downloads\jared.asc"
df = 22
dt = 1.0 / df

data = pd.read_csv(fn, index_col="Time", usecols=["data", "Time"])

tf = PlotTF(data.data.to_numpy(), df=df, plot_yn="n")
tf.freq_scale = "log"
tf.time_units = "min"
tf.tf_nh = 128
tf.tf_tstep = 8
tf.tf_L = 7
tf.fig__num = 3
# tf.tf_type = "stft"


tf.plot()
