# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 10:01:20 2019

@author: jpeacock
"""

import numpy as np
import pymc3 as pm

n= 5000
c1 = np.random.lognormal(np.log(1E-4), .15, n)
c2 = np.random.lognormal(np.log(1./5), .15, n)

expected_s1 = .85
expected_s2 = 1 - expected_s1

expected_m1 = .15
expected_m2 = 2

c_obs = (expected_s1 ** expected_m1 * c1) + (expected_s2 ** expected_m2 * c2) 

glover = pm.Model()
with glover:
    
    s1 = pm.Normal('s1', mu=.8, sd=1)
    m1 = pm.Normal('m1', mu=.15, sd=1)
    m2 = pm.Lognormal('m2', mu=0, sd=.6)
    r1 = pm.Normal('r1', mu=1E-4, sd=.02)
    r2 = pm.Normal('r2', mu=.2, sd=4)
    
    expected_mu = (s1 ** m1 * r1) + ((1 - s1) ** m2 * r2)
    
    c_measured = pm.Normal('c_measured', mu=expected_mu, 
                              observed=c_obs)
    
    trace = pm.sample(draws=5000, tune=1000, chains=1)
 
a = pm.plot_trace(trace)
print(pm.summary(trace[1000:]))
