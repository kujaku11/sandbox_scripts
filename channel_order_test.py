# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 16:01:34 2018

@author: jpeacock
"""

chn_list = ['Ex', 'Hx', 'Ey', 'Hy', 'Hz']

c_list = ['Ey', 'Hy', 'Hx']

k = []

for cc in chn_list:
    for chn in c_list:
        if cc == chn:
            k.append(cc)
            continue

