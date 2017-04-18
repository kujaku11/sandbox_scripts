# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 10:59:30 2017

@author: jpeacock
"""
import numpy as np
import mtpy.modeling.modem as modem

res_fn = r"c:\Users\jpeacock\Documents\MountainPass\modem_inv\inv_01\mp_err03_cov03_NLCG_053.res"
rms_thresh = 3.0

res_obj = modem.Data()
res_obj.read_data_file(res_fn)

lines = ['Station,Zxx,Zxy,Zyx,Zyy,Tx,Ty,Notes']
print '='*50
for r_arr in res_obj.data_array:
    nz = np.nonzero(r_arr['z'])
    z_rms = np.nanmean(r_arr['z'].__abs__()/r_arr['z_err'].real, axis=0)
    t_rms = np.nanmean(r_arr['tip'].__abs__()/r_arr['tip_err'].real, axis=0)
    
    if np.any(z_rms > rms_thresh) or np.any(t_rms > rms_thresh):
        notes = '***CHECK***'
        print '  --> check {0}'.format(r_arr['station'])
    else:
        notes = ''
    
    lines.append('{0},{1:.2f},{2:.2f},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7}'.format(
                 r_arr['station'],
                 z_rms[0, 0], 
                 z_rms[0, 1],
                 z_rms[1, 0],
                 z_rms[1, 1],
                 t_rms[0, 0],
                 t_rms[0, 1],
                 notes))
    
                 
    
    
with open(res_fn[0:-4]+'_notes.csv', 'w') as fid:
    fid.write('\n'.join(lines))