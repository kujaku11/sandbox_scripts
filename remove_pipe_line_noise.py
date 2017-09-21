# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 16:28:19 2017

@author: jpeacock
"""
#==============================================================================
# Imports
#==============================================================================
import numpy as np
import datetime
import mtpy.usgs.zen as zen
import mtpy.processing.filter as mtfilter
import scipy.signal as signal
import scipy.interpolate as interpolate
import scipy.optimize as optimize
import pandas as pd
    
#==============================================================================
# Inputs
#==============================================================================
fn = r"d:\Peacock\MTData\Umatilla\um102\um102_20170607_070018_4096_HY.Z3D"

# noise period, this is something you will have to find, should make a 
# function to do it automatically
noise_per = 5 

pad_edge = 0.10
pad_width = 0.03

#==============================================================================
# Load time series data into TS format
#==============================================================================
st = datetime.datetime.utcnow()

z1 = zen.Zen3D()
z1.read_z3d(fn)

# number of samples
n = z1.ts_obj.ts.data.size

# relative time array to correspond with data
t_arr = np.arange(0, n/z1.ts_obj.sampling_rate, 1./z1.ts_obj.sampling_rate)

#==============================================================================
# Window data and average to get the shape of 1 pulse from the pipeline
#==============================================================================
# set window length, initialize an average window array for statistical 
# analysis later 
window_len = int(noise_per*z1.ts_obj.sampling_rate)
window_num = int(z1.ts_obj.ts.data.size/window_len)
avg_window_arr = np.zeros((window_num, window_len))

pad = int(pad_edge*z1.ts_obj.sampling_rate)
pad_w = int(pad_width*z1.ts_obj.sampling_rate)
pad_num = int(pad-pad_w)
# start indexing at the beginning of the time series
index_00 = 0
index_01 = window_len

window_count = 0
while index_01 < n:
    # detrend the data using just the mean, if you use the default 'linear'
    # then you get an unwanted slope in the resulting window
    # filter the data to get rid of all the high frequency crap
    window = signal.detrend(mtfilter.low_pass(z1.ts_obj.ts.data[index_00:index_01],
                                     14,
                                     55,
                                     z1.ts_obj.sampling_rate),
                            type='constant')
                            
    # need to get rid of edge effect
    edge_polyfit = np.polyfit(np.arange((pad_num-pad_w)*2), 
                              np.append(window[-pad_num:-pad_w],
                                        window[pad_w:pad_num]), 
                              3)

    edge_polyval = np.polyval(edge_polyfit, np.arange(pad_num*2))
    window[-pad_w:] = edge_polyval[pad_num-pad_w:pad_num]
    window[0:pad_w] = edge_polyval[pad_num-pad_w:pad_num][::-1]
    
    # put the window in the array
    avg_window_arr[window_count, :] = window
   
    # reset the index values to slide down the time series
    index_00 += window_len
    index_01 += window_len
    window_count += 1

# take the median of the window, should be the same as mean, but will use it
# for robustness
avg_window = np.median(avg_window_arr, axis=0)

if np.median(avg_window) < 1E-5:
    z1.write_ascii_mt_file()
    raise ValueError('Average window is just noise, skipping {0}'.format(fn))
#==============================================================================
# For some reason the median window does not come out with the same amplitude
# as the time series so need to find the multiplication constant so the
# pseudo noise time series is the same amplitude as the data. (maybe something
# to do with filtering or averaging maybe?)
# will use a curve optimization to do that.
#==============================================================================
class PeriodicNoise(object):
    def __init__(self, t, periodic_noise):
        self.periodic_noise = periodic_noise
        self.t = t
        self.interpolate_noise()
        
    def interpolate_noise(self):
        self.noise_interp = interpolate.interp1d(self.t, 
                                                 self.periodic_noise,
                                                 bounds_error=False)
        
    def func(self, new_t, a):
        return a*self.noise_interp(new_t)

#==============================================================================
# Make a pseudo time series of just the noise and subtract from data
#==============================================================================
PN = PeriodicNoise(t_arr[0:window_len], avg_window)

pn = np.zeros(z1.ts_obj.ts.data.size)

index_00 = 0
index_01 = window_len

window_count = 0
while index_01 < n:
    if z1.metadata.ch_cmp.lower() in ['hx', 'hy', 'hz']:
        p_obj, p_cov = optimize.curve_fit(PN.func, 
                                          t_arr[0:window_len],  
                                          avg_window_arr[window_count])
        pn[index_00:index_01] = avg_window*p_obj[0]
    else:
        pn[index_00:index_01] = avg_window
   
    index_00 += window_len
    index_01 += window_len
    window_count += 1
    
index_diff = n-index_00
pn[index_00:] = avg_window[0:index_diff]        

new_ts = z1.ts_obj.ts.data-pn

#==============================================================================
# save time series as an ascii file that BIRRP can read
#==============================================================================
z1.ts_obj.ts = pd.DataFrame({'data':new_ts})
z1.write_ascii_mt_file()

et = datetime.datetime.utcnow()
time_diff = et-st

print '==> Took: {0:.2f} seconds'.format(time_diff.seconds+time_diff.microseconds*1E-6)