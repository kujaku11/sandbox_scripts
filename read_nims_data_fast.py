# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 10:03:20 2019

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import os
import numpy as np
import struct
import datetime

# =============================================================================
# constants
# =============================================================================
block_size = 131
sampling_rate = 8 ### samples/second
e_conversion_factor = 2.44141221047903e-06
h_conversion_factor = 0.01
t_conversion_factor = 70
t_offset = 18048
block_types = ('<BBBcB'+'B'*(block_size-5))

block_dict = {'soh':0,
              'block_len':1,
              'status':2,
              'gps':3,
              'sequence':4,
              'elec_temp':(5, 6),
              'box_temp':(7, 8),
              'logic':81,
              'end':130}

### make an array of index values for magnetics and electrics
indices = np.zeros((8,5), dtype=np.int)
for kk in range(8):
    ### magnetic blocks
    for ii in range(3):
        indices[kk, ii] = 9 + (kk) * 9 + (ii) * 3
    ### electric blocks
    for ii in range(2):
        indices[kk, 3+ii] = 82 + (kk) * 6 + (ii) * 3
        
# =============================================================================
# Inputs
# =============================================================================

nims_fn = r"c:\Users\jpeacock\Downloads\data_rgr022c.bnn"

# =============================================================================
# Read data
# =============================================================================
st = datetime.datetime.now()

### load in the entire file, its not too big
with open(nims_fn, 'rb') as fid:
    nims_str = fid.read()

header_list = nims_str[0:1000].split(b'\r')
begin_bit = header_list[-1].strip()[0:1]
start_index = nims_str.find(begin_bit)

header_dict = {}
for line in header_list[0:-1]:
    line = line.decode()
    if line.find('>') == 0:
        continue
    elif line.find(':') > 0:
        key, value = line.split(':', 1)
        header_dict[key] = value
    elif line.find('<--') > 0:
        value, key = line.split('<--')
        header_dict[key] = value

### read full string into an array with all same data type
data_str = nims_str[start_index:]

### read in GPS strings into a list to be parsed later
gps_str = [struct.unpack('c', data_str[ii*block_size+3:ii*block_size+4])[0]
         for ii in range(int(len(data_str)/block_size))]
gps_str = b''.join(gps_str)
gps_list = gps_str.replace(b'\xd9', b'').replace(b'\xc7', b'').split(b'$')

### read in full string as unsigned integers
data = np.frombuffer(data_str, dtype=np.uint8)

### check the size of the data, should have an equal amount of blocks
if (data.size % block_size) == 0:
    data = data.reshape((int(data.size/block_size), block_size))
else:
    print('odd number of bytes, not even blocks')

### need to pars the data
info_array = np.zeros(data.shape[0],
                      dtype=[('soh', np.int),
                             ('block_len', np.int),
                             ('status', np.int),
                             ('gps', np.int),
                             ('sequence', np.int),
                             ('elec_temp', np.float),
                             ('box_temp', np.float),
                             ('logic', np.int),
                             ('end', np.int)])    

for key, index in block_dict.items():
            if 'temp' in key:
                value = ((data[:, index[0]] * 256 + data[:, index[1]]) - t_offset)/t_conversion_factor
            else:
                value = data[:, index]
            info_array[key][:] = value
    
    
data_array = np.zeros(data.shape[0]*sampling_rate,
                      dtype=[('hx', np.float),
                             ('hy', np.float), 
                             ('hz', np.float),
                             ('ex', np.float),
                             ('ey', np.float)])

### fill the data
for cc, comp in enumerate(['hx', 'hy', 'hz', 'ex', 'ey']):
    channel_arr = np.zeros((data.shape[0], 8), dtype=np.float)
    for kk in range(sampling_rate):
        index = indices[kk, cc]
        value = (data[:, index]*256 + data[:, index+1]) * np.array([256]) + \
                data[:, index+2]
        value[np.where(value > 8388608)] -= 16777216
        channel_arr[:, kk] = value
    data_array[comp][:] = channel_arr.flatten()
    
### clean things up
### I guess that the E channels are opposite phase?
for comp in ['ex', 'ey']:
    data_array[comp] *= -1 
et = datetime.datetime.now()

tdiff = et - st
print('Took {0} seconds'.format(tdiff.total_seconds()))




    
#for count in range(max_blocks):
#    try:
#        block = data_str[count*block_size:(count+1)*block_size]
#        block_str = struct.unpack(block_types, block)
#        gps_str += block_str[block_dict['gps']]
#        if block_str[0] != 1:
#            print('Skipping block {0}'.format(count))
#            continue
#        for key,ii in block_dict.items():
#            if 'temp' in key:
#                value = ((block_str[ii[0]] * 256 + block_str[ii[1]]) - t_offset)/t_conversion_factor
#            elif key == 'sequence':
#                value = count
#            elif key == 'gps':
#                value = struct.unpack('<b', block_str[ii])[0]
#            else:
#                value = block_str[ii]
#            data_array[key][count] = value
#        
#        data_block = np.zeros((8,5))
#        for cc in range(5):
#            for kk in range(8):
#                index = indices[kk, cc]
#                value = ((block_str[index] * 256) + block_str[index+1]) * 256 + block_str[index+2]
#                data_block[kk, cc] = value
#        data_block[:, -2:] *= -1
#        
#        data_array['data'][count] = data_block
#    except Exception as error:
#        print(error)
#        break
#        
#print('read in {0} blocks'.format(count))     
#    
#gps_list = gps_str.replace(b'\xcc', b'').split(b'$')