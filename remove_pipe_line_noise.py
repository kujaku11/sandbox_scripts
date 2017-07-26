# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 16:28:19 2017

@author: jpeacock
"""
import numpy as np
import matplotlib.pyplot as plt

import mtpy.core.ts as mtts
import mtpy.usgs.zen as zen
import mtpy.imaging.plotspectrogram as plot_spectrogram
import mtpy.processing.filter as mtfilter
import scipy.signal as signal
import pandas as pd

def read_z3d(fn):
    z1 = zen.Zen3D(fn)
    z1.read_z3d()
    z1.station = '{0}{1}'.format(z1.metadata.line_name, z1.metadata.rx_xyz0[0:2])
    
    #h5_fn = r"d:\Peacock\MTData\Umatilla\hf05\hf05_20170517_193018_256_EX.h5"
    ts_obj = mtts.MT_TS()
    
    ts_obj.ts = pd.DataFrame({'data': z1.convert_counts()})
    ts_obj.station = z1.station
    ts_obj.sampling_rate = int(z1.df)
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

ts_df = ts_obj.ts

noise_per = 5

n = 2**14

#ts_filt, filt_list = mtfilter.adaptive_notch_filter(np.array(ts_obj.ts[0:n])[:, 0], 
#                                                    df=ts_obj.sampling_rate,
#                                                    notches=[30, 60, 120, 180])

# be sure to detrend the signal before processing
#ts_df['detrend'] = ts_df.apply(signal.detrend)
#ts_filt = low_pass(ts, 30, 60, 
#                   ts_obj.sampling_rate)

window_len = int(noise_per*ts_obj.sampling_rate)
avg_window = np.zeros(window_len)

index_00 = 0
index_01 = window_len

window_count = 1
while index_01 < ts_df.data.size:
    window = signal.detrend(ts_df.data[index_00:index_01])
#    avg_window += window
    avg_window += low_pass(window, 30, 60, ts_obj.sampling_rate)
    
#    if index_00 == 0:
#        avg_window[:] = window
#        
#    else:
#        lag = -1*get_max_correlation(avg_window, window)
#        # positive shift    
#        if lag >= 0:     
#            avg_window[0:window_len-lag] += window[lag:]
#        elif lag < 0:
#            avg_window[lag:] += window[:-lag]
#        avg
            
    index_00 += window_len
    index_01 += window_len
    window_count += 1
            
avg_window = avg_window/window_count

## need to figure out a way to scale the noise to match the data

## make sure the ends meet so there are no weird artifacts
#ends = np.median([avg_window[0:11], avg_window[-11:]])
#
#avg_window[0:10] = ends
#avg_window[-10:] = ends
#
#noise =


## get windows, being sure to over lap so to catch the full wave form
#index_list = []
#for ii in range(num_windows):
#    if ii == 0:
#        index_00 = 0
#        index_01 = window_len+window_overlap
#        windows[ii, window_overlap:] = ts_filt[index_00:index_01]
#    else:
#        index_00 = ii*window_len-window_overlap
#        index_01 = (ii+1)*window_len+window_overlap
#        windows[ii, :] = ts_filt[index_00:index_01]
#    index_list.append([index_00, index_01])
#
## align the windows through correlation
#avg_window = np.zeros(window_width)
#for window in windows[1:]:
#    lag_shift = -1*get_max_correlation(windows[1], window)
#
#    # positive shift    
#    if lag_shift >= 0:     
#        avg_window[0:window_width-lag_shift] += window[lag_shift:]
#    elif lag_shift < 0:
#        avg_window[lag_shift:] += window[:-lag_shift]
#    
## compute average
#avg_window = avg_window/(num_windows-1)
#
## correlate the window with the time series to get the delta functions
#xc = signal.correlate(ts_filt, avg_window)[window_width:]
#xc[np.where(xc < 0.5)] = 0
#
## get delta functions
#deltas = np.zeros_like(ts_filt)
#for ii, index in enumerate(index_list):
#    xc_window = xc[index[0]:index[1]]
#    d_index = xc_window.argmax()+ii*window_width
#    deltas[d_index] = 1
#    
#noise = signal.fftconvolve(avg_window, deltas)[0:n]
#
#ts_clean = ts_filt-noise






#spec = plot_spectrogram.PlotTF(ts_filt, 
#                               **{'df':256, 
#                                 'time_units': 'sec',
#                                 'tstep':8,
#                                 'plot_type':'all',
#                                 'font_size':9})

#ft = np.fft.fft(ts_obj.ts[0:n])
#f = np.fft.fftfreq(n, 1./ts_obj.sampling_rate)
#
#fig = plt.figure()
#
#ax = fig.add_subplot(1, 1, 1)
#ax.loglog(f, abs(ft)**2)
#ax.set_xlabel('Frequency')
#ax.set_ylabel('Power')
#
##ax2 = fig.add_subplot(2, 1, 2)
##ax2.plot(np.arange(n)/ts_obj.sampling_rate, ts_obj.ts[0:n])
##ax2.set_xlabel('time (s)')
##ax2.set_ylabel('{0}'.format(ts_obj.component))
#
#plt.show()