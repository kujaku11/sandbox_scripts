# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 13:38:01 2015

@author: jpeacock-pr
"""

import numpy as np
import matplotlib.pyplot as plt

# variables and how much they can range
x = np.arange(-10, 10, 5)
y = np.arange(-.5, .5, .1)

# model function
def model(x, y):
    return x*np.exp(-y)

# define a figure to plot things in
fig = plt.figure(1, [5,5])
ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1, 2, 2)

# cerate an empty array similar to the shape of your input variables
stat_array = np.zeros((x.shape[0], y.shape[0]))  
  
# loop over x possibilities
for ii, x_ii in enumerate(x):
    # loop over y possibilities
    for jj, y_jj in enumerate(y):
        # calculate the model given x and y
        answer = model(x_ii, y_jj)
        
        # plot the results
        ax1.plot(x_ii, answer, ls='none', marker='*')
        ax2.plot(y_jj, answer, ls='none', marker='*')
        
        # save the model into the empty array to use later for statistics
        stat_array[ii, jj] = answer

plt.show()

# calculate the standard deviation for a given x
x_0_std = stat_array[0, :].std()

print 'Standard deviation at x={0} is {1:.2f}'.format(x[0], x_0_std)

# calculate the covariance matrix of stat_array
stat_cov = np.cov(stat_array)        