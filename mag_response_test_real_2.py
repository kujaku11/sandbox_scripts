# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 16:14:10 2014

@author: jpeacock-pr
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.io as io
import scipy.signal as sps

# dt = 1./40
# t = np.arange(2**12)*dt
# nt = t.shape[0]
# ts = np.sum(np.array([amp*np.cos(ww*t*np.pi*2+phase*np.pi) for amp, ww, phase in
#                      zip(np.random.randint(0,10,nt), np.random.random(nt),
#                          np.random.rand(nt))]), axis=0)
# ts = 3*np.cos(.1*t*2*np.pi)+1*np.cos(.5*t*2*np.pi)-2*np.sin(2*t*2*np.pi+np.pi/6)


def remove_dc_trend(time_series):
    """
    remove dc component of time series
    """

    dc_trend = time_series.mean()

    return_time_series = time_series - dc_trend

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
    freq = np.fft.fftfreq(2 * len_t, dt)[0:len_t]

    # coil response in the frequency domain
    coil_resp = (
        (1.009202 * 10 ** 21)
        * freq
        / (freq + 1.21454)
        * (freq + 1.97706 * 10 ** 3 - 1.9771 * 10 ** 3 * 1j)
        * (freq + 1.97706 * 10 ** 3 + 1.9771 * 10 ** 3 * 1j)
    )

    coil_resp[0] = coil_resp[1]

    # normalize the filter response
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
    f_pad = np.zeros(2 * len_t)
    f_pad[0:len_t] = time_series

    # compute the fourier transform
    F = np.fft.fft(f_pad)[0:len_t]

    # compute the coil response
    cr, freq = coil_response(time_series, dt)

    # multiply in the fourier domain
    F_R = F * cr

    # need to make the calculated response symmetric according to the fft
    # so we need to reverse the time series to correspond to negative
    # frequencies
    F_return = np.zeros(2 * len_t, dtype="complex")
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
    f_pad = np.zeros(2 * len_t)
    f_pad[0:len_t] = time_series

    # compute the fourier transform
    F = np.fft.fft(f_pad)[0:len_t]

    # compute the coil response
    cr, freq = coil_response(time_series, dt)

    # multiply in the fourier domain
    F_R = F / cr

    # need to make the calculated response symmetric according to the fft
    # so we need to reverse the time series to correspond to negative
    # frequencies
    F_return = np.zeros(2 * len_t, dtype="complex")
    F_return[0:len_t] = F_R
    F_return[len_t:] = F_R[::-1]

    # compute the ifft
    # need a factor of 4 due to the fourier transform
    f_return = np.fft.ifft(F_return)[0:len_t]

    return f_return.real


# ==============================================================================
# try to remove the response
# ==============================================================================
# test a random signal
# ts_rand = np.random.ranf(2**10)
mat_dict = io.loadmat(r"c:\Users\jpeacock-pr\Downloads\JRSC_LT2_2007_021.mat")
ts, dc_trend = remove_dc_trend(mat_dict[sorted(mat_dict.keys())[0]][0 : 2 ** 15, 0])

dt = 1.0
nt = ts.shape[0]
t = np.arange(nt) * dt

cut_off = 0.1

# remove the response
output_convert = remove_coil_response(ts, dt)

# apply a high pass filter
b, a = sps.butter(3, cut_off / (2 * dt), btype="high")
hp_filter_output = sps.filtfilt(b, a, output_convert)

fig = plt.figure(2)
fig.clf()
ax1 = fig.add_subplot(4, 3, 1)
(l1,) = ax1.plot(t, ts, "k")

ax2 = fig.add_subplot(4, 3, 4, sharex=ax1)
(l2,) = ax2.plot(t, output_convert, "b")

ax3 = fig.add_subplot(4, 3, 7, sharex=ax1)
(l3,) = ax3.plot(t, hp_filter_output, "g")


fig.legend(
    [l1, l2, l3],
    ["input", "input-coil_response", "high_pass output"],
    loc="upper center",
    ncol=3,
)

# plot the spectrum for each time series to see what's happening
plot_freq = np.fft.fftfreq(nt, dt)[0 : nt / 2]
fft_ts = np.fft.fft(ts)[0 : nt / 2]
fft_output_coil = np.fft.fft(output_convert)[0 : nt / 2]
fft_hp = np.fft.fft(hp_filter_output)[0 : nt / 2]

ax1f = fig.add_subplot(4, 3, 2)
ax1f.loglog(plot_freq, abs(fft_ts) ** 2, "k")

ax2f = fig.add_subplot(4, 3, 5, sharex=ax1f)
ax2f.loglog(plot_freq, abs(fft_output_coil) ** 2, "b")

ax3f = fig.add_subplot(4, 3, 8, sharex=ax1f)
ax3f.loglog(plot_freq, abs(fft_hp) ** 2, "g")

ax1p = fig.add_subplot(4, 3, 3, sharex=ax1f)
ax1p.semilogx(
    plot_freq, np.rad2deg(np.unwrap(np.arctan2(fft_ts.imag, fft_ts.real))), "k"
)

ax2p = fig.add_subplot(4, 3, 6, sharex=ax1f)
ax2p.semilogx(
    plot_freq,
    np.rad2deg(np.unwrap(np.arctan2(fft_output_coil.imag, fft_output_coil.real))),
    "b",
)

ax3p = fig.add_subplot(4, 3, 9, sharex=ax1f)
ax3p.semilogx(
    plot_freq, np.rad2deg(np.unwrap(np.arctan2(fft_hp.imag, fft_hp.real))), "g"
)

ax4 = fig.add_subplot(4, 1, 4, sharex=ax1)
(l1,) = ax4.plot(t, ts, "k")
(l2,) = ax4.plot(t, output_convert, "b")
(l3,) = ax4.plot(t, hp_filter_output, "g")

for xx in [ax1, ax2, ax3, ax4]:
    xx.set_xlabel("time (s)")
    xx.set_ylabel("amplitude")
    xx.axis("tight")
    # xx.set_ylim(-2000, 2000)

for xx in [ax1f, ax2f, ax3f]:
    xx.set_xlabel("frequency (Hz)")
    xx.set_ylabel("power")
    xx.set_xlim(plot_freq.max(), plot_freq.min())
    xx.axis("tight")

for xx in [ax1p, ax2p, ax3p]:
    xx.set_xlabel("frequency (Hz)")
    xx.set_ylabel("phase")
    xx.set_xlim(plot_freq.max(), plot_freq.min())
    xx.axis("tight")

plt.show()
