# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:49:18 2020

@author: jpeacock
"""

import numpy as np
from matplotlib import pyplot as plt

x = np.arange(-1000, 1200, 100)
y = np.arange(-1200, 1500, 100)
z = np.arange(-1000, 100, 50)

sx = -250
sy = 500

res = np.zeros((x.size, y.size, z.size))
res[:, :, :] = 10

for ii in range(x.size):
    for jj in range(y.size):
        a = np.random.randint(0, 6)
        res[ii, jj, 0:a] = 20
        
x_find = np.where((sx <= x[1:]) & (sx >= x[:-1]))[0][0]
y_find = np.where((sy <= y[1:]) & (sy >= y[:-1]))[0][0]
z_find = np.amin(np.where(res[x_find, y_find, :] < 20)) 

elev = z[z_find]

fig = plt.figure(1)
ax1 = fig.add_subplot(2, 2, 1)
ax2 = fig.add_subplot(2, 2, 2, sharex=ax1)
ax3 = fig.add_subplot(2, 2, 3, sharex=ax1, sharey=ax2)

xg, yg = np.meshgrid(x, y, indexing='ij')
yzg, zyg = np.meshgrid(y, z, indexing='ij')
xzg, zxg = np.meshgrid(x, z, indexing='ij')

ax1.pcolormesh(xg, yg, res[:, :, z_find], vmin=10, vmax=20)
ax2.pcolormesh(xzg, zxg, res[:, y_find, :], vmin=10, vmax=20)
ax3.pcolormesh(yzg, zyg, res[x_find, :, :], vmin=10, vmax=20)

ax1.scatter(sx, sy, marker = 'o', s=30, c='cyan')
ax2.scatter(sx, elev, marker = 'o', s=30, c='cyan')
ax3.scatter(sy, elev, marker = 'o', s=30, c='cyan')

ax1.set_xlabel('Easting')
ax2.set_xlabel('Easting')
ax1.set_ylabel('Northing')
ax3.set_xlabel('Northing')


ax2.set_ylim((z.max(), z.min()))



plt.show()
            

