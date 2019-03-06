# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 14:24:18 2019

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt

# make a with a hole in the middle
box = np.zeros((25, 25))
box[10:15, 10:15] = 1

# compute the FFT
box_fft = np.fft.fft2(box)

# fold the FFT
box_folded = np.fft.fftshift(box_fft.copy())

# Plot data
fig = plt.figure(1)
ax1 = fig.add_subplot(1, 2, 1)
im1 = ax1.imshow(abs(box_fft))
ax1.set_title('Raw FFT')
plt.colorbar(im1, ax=ax1, shrink=.5)

ax2 = fig.add_subplot(1, 2, 2, sharex=ax1, sharey=ax1)
im2 = ax2.imshow(abs(box_folded))
ax2.set_title('Folded FFT')
plt.colorbar(im2, ax=ax2, shrink=.5)

plt.show()
