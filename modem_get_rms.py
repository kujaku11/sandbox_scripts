# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 10:59:30 2017

@author: jpeacock
"""

import numpy as np
import mtpy.modeling.modem as modem
import pandas as pd

res_fn = r"c:\Users\jpeacock\Documents\iMush\modem_inv\paul\imush_fin_hp_L100_NLCG_011.res"
rms_thresh = 5.0

res_obj = modem.Data()
res_obj.read_data_file(res_fn)

def write_rms_file(res_obj, rms_thresh=5.0):
    """
    write summary files
    """
    keys = ['Station' , 'lat', 'lon', 'Z', 'T', 'Zxx', 'Zxy', 'Zyx' , 'Zyy',
            'Tx', 'Ty', 'Notes']
    rms_dict = dict([(key, []) for key in keys])
    for r_arr in res_obj.data_array:
        r_arr['z'][np.where(r_arr['z']) == 0] = np.nan
        r_arr['z_err'][np.where(r_arr['z']) == 0] = np.nan
        r_arr['tip'][np.where(r_arr['tip']) == 0] = np.nan
        r_arr['tip_err'][np.where(r_arr['tip']) == 0] = np.nan

        z_rms = np.nanmean(r_arr['z'].__abs__()/r_arr['z_err'].real,
                           axis=0)
        t_rms = np.nanmean(r_arr['tip'].__abs__()/r_arr['tip_err'].real,
                           axis=0)
        
        if np.any(z_rms > rms_thresh) or np.any(t_rms > rms_thresh):
            notes = '***CHECK***'
            print('  --> check {0}'.format(r_arr['station']))
        else:
            notes = ''
        
        rms_list = [r_arr['station'], r_arr['lat'], r_arr['lon'], z_rms.mean(),
                     t_rms.mean(), z_rms[0, 0], z_rms[0, 1], z_rms[1, 0],
                     z_rms[1, 1], t_rms[0, 0], t_rms[0, 1], notes]
        for key, rms_value in zip(keys, rms_list):
            rms_dict[key].append(rms_value)
        
    df = pd.DataFrame(rms_dict)
        
    return res_fn[0:-4]+'rms__notes.csv'

def read_rms_file(rms_fn):
    """
    read in RMS file as a pandas database
    """
    df = pd.DataFrame(rms_fn)
    
    return df



