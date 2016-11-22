# -*- coding: utf-8 -*-
"""
Created on Wed May 25 10:48:11 2016

@author: jpeacock
"""

import mtpy.core.z as mtz
import numpy as np


f1 = r"c:\Users\jpeacock\Documents\ShanesBugs\Sev_MT_Final_ga\MT001.edi"

with open(f1, 'r') as fid:
    data_lines = fid.readlines()[102:]
    
data_dict = {}
data_find = False
for line in data_lines:
    if line.find('>') >= 0 and line.find('!') == -1:
        line_list = line[1:].strip().split()
        key = line_list[0].lower()
        if key[0] == 'z' or key[0] == 't' or key == 'freq':
            data_find = True
            data_dict[key] = []
        else:
            data_find = False
        

    elif data_find == True and line.find('>') == -1 and line.find('!') == -1:
        d_lines = line.strip().split()
        for ii, dd in enumerate(d_lines):
            # check for empty values and set them to 0, check for any
            # other characters sometimes there are ****** for a null
            # component
            try:
                d_lines[ii] = float(dd)
                if d_lines[ii] == 1.0e32:
                    d_lines[ii] = 0.0
            except ValueError:
                d_lines[ii] = 0.0
        data_dict[key] += d_lines

## fill useful arrays
freq_arr = np.array(data_dict['freq'], dtype=np.float)

## fill impedance tensor
z_obj = mtz.Z()
z_obj.freq = freq_arr.copy()
z_obj.z = np.zeros((freq_arr.size, 2, 2), dtype=np.complex)
z_obj.z_err = np.zeros((freq_arr.size, 2, 2), dtype=np.float)
try:
    z_obj.rotation_angle = data_dict['zrot']
except KeyError:
    z_obj.rotation_angle = np.zeros_like(freq_arr)

z_obj.z[:, 0, 0] = np.array(data_dict['zxxr'])+\
                     np.array(data_dict['zxxi'])*1j
z_obj.z[:, 0, 1] = np.array(data_dict['zxyr'])+\
                    np.array(data_dict['zxyi'])*1j
z_obj.z[:, 1, 0] = np.array(data_dict['zyxr'])+\
                    np.array(data_dict['zyxi'])*1j
z_obj.z[:, 1, 1] = np.array(data_dict['zyyr'])+\
                    np.array(data_dict['zyyi'])*1j

z_obj.z_err[:, 0, 0] = np.array(data_dict['zxx.var'])
z_obj.z_err[:, 0, 1] = np.array(data_dict['zxy.var'])
z_obj.z_err[:, 1, 0] = np.array(data_dict['zyx.var'])
z_obj.z_err[:, 1, 1] = np.array(data_dict['zyy.var'])
