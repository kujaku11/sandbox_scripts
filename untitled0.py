# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 12:01:06 2019

@author: jpeacock
"""

import numpy as np
from matplotlib import pyplot as plt
from mtpy.modeling import modem

mfn = r"c:\Users\jpeacock\Documents\Geysers\modem_inv\inv03\gz_err03_cov02_NLCG_057.rho"

rho = 45

m_obj = modem.Model()
m_obj.read_model_file(mfn)

