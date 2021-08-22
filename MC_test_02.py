# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 14:22:37 2015

@author: jpeacock-pr
"""

import pymc
import numpy as np
import matplotlib.pyplot as plt


x = np.arange(-5, 5, 1)

# these are the data that you have from experimentation
# for now we'll just make a line with normal distributed error
data = 1.5 * x + 1 + np.random.random(x.shape) * 0.05


# now we have a model with input variables for instance
# a straight line is y = mx+b where the independent variable is x and m and
# b might vary.  These need to be represented as distributions
# for a monte-carlo approximation to work

# define the m as being a normal distribution around the center 5, it has
# a width (scale) of 5 and has 6 data points (size)
m = pymc.Normal("m", 0, 0.5)

# define b as also being a normal distribution around a center of 0
# a width (scale) of 2 and size of 4 data points
b = pymc.Normal("b", 0, 0.05)

# our observations are also represented as a distribution
x_obs = pymc.Normal("x", 0, 1, value=x, observed=True)

# a straight line is deterministic so we make it a deterministic object
# to do this a fancy way is to use a decorator, that just means that
# the defined function is turned into a deterministic object
@pymc.deterministic
def line(slope=m, y_intercept=b, x_data=x_obs):
    return slope * x_data + y_intercept


# now we want to model the observed values
y = pymc.Normal("y", line, value=data, observed=True)
#
model = pymc.Model([line, m, b, y, x_obs])

# run a MCMC over the parameters and model
mcmc = pymc.MCMC(model)

# run 1000 different models but only keep 1/2 of them
mcmc.sample(10000, thin=1)

print "mean of the slope is {0:.2f}".format(np.mean(mcmc.trace("m")[:]))

# plot a histogram of the slope
fig = plt.figure(1)
ax1 = fig.add_subplot(1, 2, 1)
ax1.hist(mcmc.trace("m")[:], bins=50)
ax1.set_xlabel("Slope value")
ax1.set_ylabel("Counts")

ax2 = fig.add_subplot(1, 2, 2)
ax2.hist(mcmc.trace("b")[:], bins=50)
ax2.set_xlabel("y-intercept")
ax2.set_ylabel("Counts")

print mcmc.summary()

plt.show()
