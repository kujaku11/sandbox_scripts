# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 17:38:25 2019

@author: jpeacock
"""
import numpy as np
from mtpy.core import mt

m1 = mt.MT(r"c:\Users\jpeacock\Documents\edi_folders\rgr_release_edi\rgr120.edi")

### estimate levearge points, or outliers
res = m1.Z.phase_xx
### estimate the median
med = np.median(res)
### locate the point closest to the median
tol = np.abs(res-np.median(res)).min()
m_index = np.where((res-med >= tol*.95) & (res-med <= tol*1.05))[0][0]
r_index = m_index + 1

bad_points = []
# go to the right
while r_index < res.shape[0]:
    r0 = res[r_index-1]
    r1 = res[r_index]
    if abs(r1-r0) > np.cos(np.pi/4)*r0:
        bad_points.append(r_index)
    r_index += 1
    
# go to the left
l_index = m_index - 1
while l_index > -1:
    r0 = res[l_index-1]
    r1 = res[l_index]
    if abs(r1-r0) > np.cos(np.pi/4)*r0:
        bad_points.append(l_index)
    l_index -= 1
    
print(bad_points)