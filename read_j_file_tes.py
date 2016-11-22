# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 13:09:38 2016

@author: jpeacock
"""
import numpy as np
import mtpy.core.z as mtz
j_fn = r"d:\Peacock\MTData\MonoBasin\MB_June2015\mb300\TS\BF\16\300.j"

with open(j_fn, 'r') as fid:
    j_lines = fid.readlines()
    
# read header lines

header_lines = [j_line for j_line in j_lines if '#' in j_line]
metadata_lines = [j_line for j_line in j_lines if '>' in j_line]
data_lines = [j_line for j_line in j_lines if not '>' in j_line and not '#' in j_line][1:]
del j_lines

header_dict = {'title':header_lines[0][1:].strip()}
fn_count = 0
theta_count = 0
# put the information into a dictionary 
for h_line in header_lines[1:]:
    # replace '=' with a ' ' to be sure that when split is called there is a
    # split, especially with filenames
    h_list = h_line[1:].strip().replace('=', ' ').split()
    # skip if there is only one element in the list
    if len(h_list) == 1:
        continue
    # get the key and value for each parameter in the given line
    for h_index in range(0, len(h_list), 2):
        h_key = h_list[h_index]
        # if its the file name, make the dictionary value be a list so that 
        # we can append nread and nskip to it, and make the name unique by
        # adding a counter on the end
        if h_key == 'filnam':
            h_key = '{0}_{1:02}'.format(h_key, fn_count)
            fn_count += 1
            h_value = [h_list[h_index+1]]
            header_dict[h_key] = h_value
            continue
        elif h_key == 'nskip' or h_key == 'nread':
            h_key = 'filnam_{0:02}'.format(fn_count-1)
            h_value = int(h_list[h_index+1])
            header_dict[h_key].append(h_value)
            
        # if its the line of angles, put them all in a list with a unique key
        elif h_key == 'theta1':
            h_key = '{0}_{1:02}'.format(h_key, theta_count)
            theta_count += 1
            h_value = float(h_list[h_index+1])
            header_dict[h_key] = [h_value]
        elif h_key == 'theta2' or h_key == 'phi':
            h_key = '{0}_{1:02}'.format('theta1', theta_count-1)
            h_value = float(h_list[h_index+1])
            header_dict[h_key].append(h_value)
            
        else:
            try:
                h_value = float(h_list[h_index+1])
            except ValueError:
                h_value = h_list[h_index+1]
            
            header_dict[h_key] = h_value

metadata_dict = {}
for m_line in metadata_lines:
    m_list = m_line.strip().split('=')
    m_key = m_list[0][1:].strip().lower()
    try:
        m_value = float(m_list[0].strip())
    except ValueError:
        m_value = 0.0
        
    metadata_dict[m_key] = m_value

# read data
z_index_dict = {'zxx':(0, 0),
                'zxy':(0, 1),
                'zyx':(1, 0),
                'zyy':(1, 1)}
t_index_dict = {'tzx':(0, 0),
                'tzy':(0, 1)}
                
# sometimes birrp outputs some missing periods, so the best way to deal with 
# this that I could come up with was to get things into dictionaries with 
# key words that are the period values, then fill in Z and T from there
# leaving any missing values as 0

# make empty dictionary that have keys as the component 
z_dict = dict([(z_key, {}) for z_key in z_index_dict.keys()])
t_dict = dict([(t_key, {}) for t_key in t_index_dict.keys()])
for d_line in data_lines:
    # check to see if we are at the beginning of a component block, if so 
    # set the dictionary key to that value
    if 'z' in d_line.lower():
        d_key = d_line.strip().split()[0].lower()
    
    # if we are at the number of periods line, skip it
    elif len(d_line.strip().split()) == 1:
        continue
    # get the numbers into the correct dictionary with a key as period and
    # for now we will leave the numbers as a list, which we will parse later
    else:
        # split the line up into each number
        d_list = d_line.strip().split()
        
        # make a copy of the list to be sure we don't rewrite any values,
        # not sure if this is necessary at the moment
        d_value_list = list(d_list)
        for d_index, d_value in enumerate(d_list):
            # check to see if the column number can be converted into a float
            # if it can't, then it will be set to 0, which is assumed to be
            # a masked number when writing to an .edi file
            try:
                d_value_list[d_index] = float(d_value)
            except ValueError:
                d_value_list[d_index] = 0.0
        
        # put the numbers in the correct dictionary as:
        # key = period, value = [real, imaginary, error]
        if d_key in z_index_dict.keys():
            z_dict[d_key][d_value_list[0]] = d_value_list[1:4]
        elif d_key in t_index_dict.keys():
            t_dict[d_key][d_value_list[0]] = d_value_list[1:4]
            
# now we need to get the set of periods for all components
all_periods = sorted(list(set(np.array([z_dict[z_key].keys() for z_key in z_index_dict.keys()]+\
                            [t_dict[t_key].keys() for t_key in t_index_dict.keys()]).flatten())))

num_per = len(all_periods)

# fill arrays
z_arr = np.zeros((num_per, 2, 2), dtype=np.complex)
z_err_arr = np.zeros((num_per, 2, 2), dtype=np.float)

t_arr = np.zeros((num_per, 1, 2), dtype=np.complex)
t_err_arr = np.zeros((num_per, 1, 2), dtype=np.float)

for p_index, per in enumerate(all_periods):
    for z_key in sorted(z_index_dict.keys()):
        kk = z_index_dict[z_key][0]
        ll = z_index_dict[z_key][1]
        z_value = z_dict[z_key][per][0]+1j*z_dict[z_key][per][1]
        z_arr[p_index, kk, ll] = z_value
        z_err_arr[p_index, kk, ll] = z_dict[z_key][per][2]
    for t_key in sorted(t_index_dict.keys()):
        kk = t_index_dict[t_key][0]
        ll = t_index_dict[t_key][1]
        t_value = t_dict[t_key][per][0]+1j*t_dict[t_key][per][1]
        t_arr[p_index, kk, ll] = t_value
        t_err_arr[p_index, kk, ll] = t_dict[t_key][per][2]

# put the results into mtpy objects
freq = 1./np.array(all_periods)    
z_obj = mtz.Z(z_arr, z_err_arr, freq)
t_obj = mtz.Tipper(t_arr, t_err_arr, freq)    