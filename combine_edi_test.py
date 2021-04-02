# -*- coding: utf-8 -*-
"""
Created on Fri Sep 09 14:24:29 2016

@author: jpeacock-pr
"""
import mtpy.core.edi as mtedi
import numpy as np

edi_fn_list = [r"c:\MT\MSHS\ms33\TS\BF\4096\MB000.edi", 
               r"c:\MT\MSHS\ms33\TS\BF\1024\MB000.edi", 
               r"c:\MT\MSHS\ms33\TS\BF\256\MB000.edi", 
               r"c:\MT\MSHS\ms33\TS\BF\16\MB000.edi"]



sr_dict={4096 : (1000., 4),
         1024 : (3.99, 1.),
         256 : (.99, .04),
         16 : (.039, .0001)} 
        
        
data_arr = np.zeros(100, 
                    dtype=[('freq', np.float),
                           ('z', (np.complex, (2, 2))),
                           ('z_err', (np.float, (2, 2))), 
                           ('tipper', (np.complex, (2, 2))),
                           ('tipper_err', (np.float, (2, 2)))])
                           
count = 0
for edi_fn in edi_fn_list:
    edi_obj = mtedi.Edi(edi_fn)
    # get sampling rate from directory path
    for fkey in sorted(sr_dict.keys(), reverse=True):
        if str(fkey) in edi_fn:
            # locate frequency range
            f_index = np.where((edi_obj.Z.freq >= sr_dict[fkey][1]) & 
                               (edi_obj.Z.freq <= sr_dict[fkey][0]))
                               
                               
            data_arr['freq'][count:count+len(f_index[0])] = edi_obj.Z.freq[f_index]
            data_arr['z'][count:count+len(f_index[0])] = edi_obj.Z.z[f_index]
            data_arr['z_err'][count:count+len(f_index[0])] = edi_obj.Z.z_err[f_index]
            if edi_obj.Tipper.tipper is not None:                    
                data_arr['tipper'][count:count+len(f_index[0])] = edi_obj.Tipper.tipper[f_index]
                data_arr['tipper_err'][count:count+len(f_index[0])] = edi_obj.Tipper.tipper_err[f_index]

            count += len(f_index[0])
            
# now replace
data_arr = data_arr[np.nonzero(data_arr['freq'])]
sort_index = np.argsort(data_arr['freq'])

# check to see if the sorted indexes are descending or ascending,
# make sure that frequency is descending
if data_arr['freq'][0] > data_arr['freq'][1]:
    sort_index = sort_index[::-1]
    
data_arr = data_arr[sort_index]
new_z = mtedi.MTz.Z(data_arr['z'],
                    data_arr['z_err'],
                    data_arr['freq'])
                    
if np.all(data_arr['tipper'] != 0.0) == True:
    new_t = mtedi.MTz.Tipper(data_arr['tipper'], 
                             data_arr['tipper_err'],
                             data_arr['freq'])
                 
else:
    new_t = mtedi.MTz.Tipper()
    
edi_obj = mtedi.Edi(edi_fn_list[0])
edi_obj.Z = new_z
edi_obj.Tipper = new_t

edi_obj.write_edi_file(new_edi_fn=r"c:\MT\MSHS\ms33\TS\ms33_comb.edi")