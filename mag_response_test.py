# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 16:14:10 2014

@author: jpeacock-pr
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.io as io
#dt = 1./40
#t = np.arange(2**12)*dt
#nt = t.shape[0]
#ts = np.sum(np.array([amp*np.cos(ww*t*np.pi*2+phase*np.pi) for amp, ww, phase in
#                      zip(np.random.randint(0,10,nt), np.random.random(nt),
#                          np.random.rand(nt))]), axis=0)
#ts = 3*np.cos(.1*t*2*np.pi)+1*np.cos(.5*t*2*np.pi)-2*np.sin(2*t*2*np.pi+np.pi/6)

mat_dict = io.loadmat(r"c:\Users\jpeacock-pr\Downloads\JRSC_LT2_2007_021.mat")
ts = mat_dict[sorted(mat_dict.keys())[0]][:, 0]
dt = 1.
nt = ts.shape[0]
t = np.arange(nt)*dt

def remove_dc_trend(time_series):
    """
    remove dc component of time series
    """
    
    dc_trend = time_series.mean()
    
    return_time_series = time_series-dc_trend
    
    return return_time_series, dc_trend

def coil_response(time_series, dt):
    """
    calculate the coil response from a time series for only positive frequency
    """
    # get length of the time series
    len_t = time_series.shape[0] 
    
    # need to be sure the frequency is the correct length so that one
    # periodic section is the same lenght as the time series so we don't
    # lose information
    freq = np.fft.fftfreq(2*len_t, dt)[0:len_t]
    
    #coil response in the frequency domain
    coil_resp = (1.009202*10**21)*freq/(freq+1.21454)*\
                (freq+1.97706*10**3-1.9771*10**3*1j)*\
                (freq+1.97706*10**3+1.9771*10**3*1j)
                
    coil_resp[0] = coil_resp[1]
    
    #normalize the filter response
    coil_resp /= coil_resp.max()
                
    return coil_resp, freq
    
def add_coil_response(time_series, dt):
    """
    add a coil response to a time series in the frequency domain 
    """
    
    # compute length of time series 
    len_t = time_series.shape[0]
    
    # need to pad the time series with zeros to 2 times the original length
    # so that we don't lose information 
    f_pad = np.zeros(2*len_t)
    f_pad[0:len_t] = time_series
    
    # compute the fourier transform
    F = np.fft.fft(f_pad)[0:len_t]
    
    # compute the coil response
    cr, freq = coil_response(time_series, dt)
    
    # multiply in the fourier domain
    F_R = F*cr
    
    # need to make the calculated response symmetric according to the fft
    # so we need to reverse the time series to correspond to negative 
    # frequencies
    F_return = np.zeros(2*len_t, dtype='complex')
    F_return[0:len_t] = F_R
    F_return[len_t:] = F_R[::-1]
    
    # compute the ifft
    f_return = np.fft.ifft(F_return)[0:len_t]
    
    return f_return.real
    
def remove_coil_response(time_series, dt):
    """
    remove the coil response in the frequency domain and return the time
    series in the time domain
    """
    
    # compute length of time series 
    len_t = time_series.shape[0]
    
    # need to pad the time series with zeros to 2 times the original length
    # so that we don't lose information 
    f_pad = np.zeros(2*len_t)
    f_pad[0:len_t] = time_series
    
    # compute the fourier transform
    F = np.fft.fft(f_pad)[0:len_t]
    
    # compute the coil response
    cr, freq = coil_response(time_series, dt)
    
    
    
    # multiply in the fourier domain
    F_R = F/cr
    
    # need to make the calculated response symmetric according to the fft
    # so we need to reverse the time series to correspond to negative 
    # frequencies
    F_return = np.zeros(2*len_t, dtype='complex')
    F_return[0:len_t] = F_R
    F_return[len_t:] = F_R[::-1]
    
    # compute the ifft
    # need a factor of 4 due to the fourier transform
    f_return = 4*np.fft.ifft(F_return)[0:len_t]
    
    return f_return.real
    
#==============================================================================
# try to remove the response    
#==============================================================================

# compute a synthetic response
f_resp = add_coil_response(ts, dt)

# remove the response
f_remove = remove_coil_response(f_resp, dt)

fig = plt.figure(1)
ax1 = fig.add_subplot(3,2,1)
l1, = ax1.plot(t, ts, 'k')

ax2 = fig.add_subplot(3, 2, 3, sharex=ax1)
l2, = ax2.plot(t, f_resp, 'b')

ax3 = fig.add_subplot(3, 2, 5, sharex=ax1)
ax3.plot(t, ts, 'k')
l3, = ax3.plot(t, remove_dc_trend(f_remove)[0], 'r')

fig.legend([l1, l2, l3], 
          ['original', 'original+coil response', 'removed coil response'],
          loc='upper center', ncol=3)

# plot the spectrum for each time series to see what's happening          
plot_freq = np.fft.fftfreq(2*nt, dt)[0:nt]

ax1f = fig.add_subplot(3, 2, 2)
ax1f.loglog(plot_freq, abs(np.fft.fft(ts)[0:nt])**2, 'k')

ax2f = fig.add_subplot(3, 2, 4, sharex=ax1f)
ax2f.loglog(plot_freq, abs(np.fft.fft(f_resp)[0:nt])**2, 'b')

ax3f = fig.add_subplot(3, 2, 6, sharex=ax1f)
ax3f.loglog(plot_freq, abs(np.fft.fft(f_remove)[0:nt])**2, 'r')
ax3f.loglog(plot_freq, abs(np.fft.fft(ts)[0:nt])**2, 'k')


for xx in [ax1, ax2, ax3]:
    xx.set_xlabel('time (s)')
    xx.set_ylabel('amplitude')
    xx.axis('tight')
    #xx.set_ylim(-2000, 2000)
    
for xx in [ax1f, ax2f, ax3f]:
    xx.set_xlabel('frequency (Hz)')
    xx.set_ylabel('power')
    xx.axis('tight')    
          
plt.show()
