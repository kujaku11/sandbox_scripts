# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 15:51:02 2019

@author: jpeacock
"""

from scipy import signal
import numpy as np

import matplotlib.pyplot as plt

from mtpy.modeling import modem

fn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_07\mp_z03_c03_159.rho"
radius = 9
sigma = 2**2
        
m = modem.Model()
m.read_model_file(fn)

gx, gy = np.mgrid[-radius:radius+1, 
                  -radius:radius+1]
                      
gauss = (1./(2*np.pi*sigma))*np.exp(-((gx**2)+(gy**2))/(2*sigma))

s = signal.convolve(m.res_model[:, :, 30], gauss, mode='same')

fig = plt.figure(1)
fig.clf()
ax_01 = fig.add_subplot(1, 3, 1)
im = ax_01.imshow(np.log10(m.res_model[:, :, 35]), vmin=0, vmax=4, cmap='jet_r')

ax_02 = fig.add_subplot(1, 3, 2)
im2 = ax_02.imshow(np.log10(s), vmin=0, vmax=4, cmap='jet_r')

ax_03 = fig.add_subplot(1, 3, 3)
im3 = ax_03.imshow(gauss)
plt.colorbar(im3, ax=ax_03)

plt.show()
