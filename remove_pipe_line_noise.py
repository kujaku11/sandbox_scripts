# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 16:28:19 2017

@author: jpeacock
"""
import numpy as np
#import matplotlib.pyplot as plt

import mtpy.core.ts as mtts
import mtpy.usgs.zen as zen
#import mtpy.imaging.plotspectrogram as plot_spectrogram
#import mtpy.processing.filter as mtfilter
import scipy.signal as signal
import scipy.interpolate as interpolate
import scipy.optimize as optimize
import pandas as pd

def read_z3d(fn):
    z1 = zen.Zen3D(fn)
    z1.read_z3d()
    z1.station = '{0}{1}'.format(z1.metadata.line_name, z1.metadata.rx_xyz0[0:2])
    
    #h5_fn = r"d:\Peacock\MTData\Umatilla\hf05\hf05_20170517_193018_256_EX.h5"
    ts_obj = mtts.MT_TS()
    
    ts_obj.ts = pd.DataFrame({'data': z1.convert_counts()})
    ts_obj.station = z1.station
    ts_obj.sampling_rate = float(z1.df)
    ts_obj.start_time_utc = z1.zen_schedule
    ts_obj.n_samples = int(z1.time_series.size)
    ts_obj.component = z1.metadata.ch_cmp
    ts_obj.coordinate_system = 'geomagnetic'
    ts_obj.dipole_length = float(z1.metadata.ch_length)
    ts_obj.azimuth = float(z1.metadata.ch_azimuth)
    ts_obj.units = 'mV'
    ts_obj.lat = z1.header.lat
    ts_obj.lon = z1.header.long
    ts_obj.datum = 'WGS84'
    ts_obj.data_logger = 'Zonge Zen'
    ts_obj.instrument_num = None
    ts_obj.calibration_fn = None
    ts_obj.declination = 3.6
    
    return ts_obj
    
#==============================================================================
# try to remove pipeline noise 
#==============================================================================
def get_max_correlation(x, y):
    xc = signal.correlate(x, y)
    lag = xc.argmax()-len(x)+1
    return lag
    
def low_pass(f, low_pass_freq, cutoff_freq, sampling_rate):
    nyq = .5*sampling_rate
    filt_order, wn = signal.buttord(low_pass_freq/nyq, 
                                    cutoff_freq/nyq, 
                                    3, 40)
                                    
    b, a = signal.butter(filt_order, wn, btype='low')
    f_filt = signal.filtfilt(b, a, f)
    
    return f_filt
    
fn = r"d:\Peacock\MTData\Umatilla\um102\um102_20170606_230518_256_HX.Z3D"
ts_obj = read_z3d(fn)
n = ts_obj.ts.data.size
t_arr = np.arange(0, n/ts_obj.sampling_rate, 1./ts_obj.sampling_rate)

noise_per = 5

window_len = int(noise_per*ts_obj.sampling_rate)
avg_window = np.zeros(window_len)
window_num = int(ts_obj.ts.data.size/window_len)
avg_window_arr = np.zeros((window_num, window_len))

index_00 = 0
index_01 = window_len

window_count = 1
while index_01 < n:
    # detrend the data using just the mean, if you use the default 'linear'
    # then you get an unwanted slope in the resulting window
    # filter the data to get rid of all the high frequency crap
    window = signal.detrend(low_pass(ts_obj.ts.data[index_00:index_01],
                                     14,
                                     55,
                                     ts_obj.sampling_rate),
                            type='constant')
                            
    # need to get rid of edge effect
    edge_polyfit = np.polyfit(np.arange(60), 
                              np.append(window[-35:-5], window[5:35]), 
                              3)

    edge_polyval = np.polyval(edge_polyfit, np.arange(70))
    window[-11:] = edge_polyval[24:35]
    window[0:11] = edge_polyval[35:46]
    
    avg_window_arr[window_count-1, :] = window
   
    index_00 += window_len
    index_01 += window_len
    window_count += 1

avg_window = np.median(avg_window_arr, axis=0)

# try to fit the periodic noise to the data
class PeriodicNoise(object):
    def __init__(self, periodic_noise, t):
        self.periodic_noise = periodic_noise
        self.t = t
        self.interpolate_noise()
        
    def interpolate_noise(self):
        self.noise_interp = interpolate.interp1d(self.t, self.periodic_noise)
        
    def func(self, new_t, a):
        return a*self.noise_interp(new_t)

PN = PeriodicNoise(avg_window, t_arr[0:window_len])
a_num = 20
da = window_num/a_num
a_arr = np.zeros(a_num)
for ii, aa in enumerate(np.arange(0, window_num-da, da)):
    p_obj, p_cov = optimize.curve_fit(PN.func, 
                                      t_arr[0:window_len],  
                                      avg_window_arr[aa])
    a_arr[ii] = p_obj[0]

multiplier = a_arr.max()
# make a periodic noise signal
pn = np.zeros(ts_obj.ts.data.size)

index_00 = 0
index_01 = window_len

window_count = 1
while index_01 < n:
    pn[index_00:index_01] = avg_window*multiplier
   
    index_00 += window_len
    index_01 += window_len
    window_count += 1
    
index_diff = n-index_00
pn[index_00:] = window[0:index_diff]        

new_ts = ts_obj.ts.data-pn
