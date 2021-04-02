# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 17:11:39 2019

@author: jpeacock
"""

import numpy as np
import pymc3 as pm

with pm.Model() as model:
    s1 = pm.Lognormal("s1", mu=0.01, sigma=0.1)
    m1 = pm.Normal("m1", mu=1.5, sigma=0.5)
    p1 = pm.Normal("p1", mu=0.8, sigma=0.2)
