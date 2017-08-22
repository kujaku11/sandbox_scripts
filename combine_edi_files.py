# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 12:50:14 2017

@author: jpeacock
"""
import os
import numpy as np
import mtpy.core.edi as mtedi


edi_fn_list = [r"d:\Peacock\MTData\Geysers\gz16\TS\BF\{0}\gz16.edi".format(ii) 
               for ii in ['4096', '256', '16']]

sr_dict = {4096:(2000, 4), 
          256:(3.9, .69), 
          16:(.7, .00001)}
data_arr = np.zeros(100, 
                    dtype=[('freq', np.float),
                           ('z', (np.complex, (2, 2))),
                           ('z_err', (np.float, (2, 2))), 
                           ('tipper', (np.complex, (2, 2))),
                           ('tipper_err', (np.float, (2, 2)))])
                           
count = 0
for edi_fn in edi_fn_list:
    # get sampling rate
    fn_list = edi_fn[edi_fn.find('BF'):].split(os.path.sep)
    for ss in fn_list:
        try:
            sr_key = int(ss)
            break
        except ValueError:
            pass
    if sr_key in sr_dict.keys():         
        try:
            edi_obj = mtedi.Edi(edi_fn)

            f_index = np.where((edi_obj.Z.freq >= sr_dict[sr_key][1]) & 
                               (edi_obj.Z.freq <= sr_dict[sr_key][0]))
                               
            print sr_key, edi_obj.Z.freq[f_index]                   
            data_arr['freq'][count:count+len(f_index[0])] = edi_obj.Z.freq[f_index]
            data_arr['z'][count:count+len(f_index[0])] = edi_obj.Z.z[f_index]
            data_arr['z_err'][count:count+len(f_index[0])] = edi_obj.Z.z_err[f_index]
            if edi_obj.Tipper.tipper is not None:                    
                data_arr['tipper'][count:count+len(f_index[0])] = edi_obj.Tipper.tipper[f_index]
                data_arr['tipper_err'][count:count+len(f_index[0])] = edi_obj.Tipper.tipper_err[f_index]
    
            count += len(f_index[0])
        except IndexError:
            print 'Something went wrong with processing {0}'.format(edi_fn)
    else:
        print '{0} was not in combining dictionary'.format(sr_key)
        
            
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

# check for all zeros in tipper, meaning there is only 
# one unique value                    
if np.unique(data_arr['tipper']).size > 1:
    new_t = mtedi.MTz.Tipper(data_arr['tipper'], 
                             data_arr['tipper_err'],
                             data_arr['freq'])
                 
else:
    new_t = mtedi.MTz.Tipper()
    
edi_obj = mtedi.Edi(edi_fn_list[0])
edi_obj.Z = new_z
edi_obj.Tipper = new_t
edi_obj.Data_sect.nfreq = new_z.z.shape[0]

n_edi_fn = r"d:\Peacock\MTData\Geysers\gz16\TS\gz16_comb.edi"        
n_edi_fn = edi_obj.write_edi_file(new_edi_fn=n_edi_fn)
