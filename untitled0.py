# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 10:01:20 2019

@author: jpeacock
"""

import numpy as np
import pymc3 as pm

n = 500
c1 = np.random.lognormal(10e-8, 0.01, n)
c2 = np.random.lognormal(50, 5, n)

s1 = 0.85
s2 = 1 - s1

m1 = 0.05
m2 = 2
