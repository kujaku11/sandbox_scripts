# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 10:59:30 2017

@author: jpeacock
"""
import os
import numpy as np
import mtpy.modeling.modem as modem

#res_dir = r"c:\Users\jpeacock\Documents\iMush\modem_inv\paul"
#fn = "LC_100_NLCG_001.res"
#
#for folder in ['LC_{0}'.format(ii) for ii in [1, 5, 10, 30, 100]]:

#res_fn = os.path.join(res_dir, folder, fn)
res_fn = r"c:\Users\jpeacock\Documents\iMush\modem_inv\paul\imush_fin_hp_L100_NLCG_011.res"
rms_thresh = 5.0

res_obj = modem.Data()
res_obj.read_data_file(res_fn)

lines = ['Station,lat,lon,Z,T,Zxx,Zxy,Zyx,Zyy,Tx,Ty,Notes']
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
    
    lines.append('{0},{1:.5f},{2:.5f},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7:.2f},{8:.2f},{9:.2f},{10:.2f},{11}'.format(
                 r_arr['station'],
                 r_arr['lat'],
                 r_arr['lon'],
                 z_rms.mean(),
                 t_rms.mean(),
                 z_rms[0, 0], 
                 z_rms[0, 1],
                 z_rms[1, 0],
                 z_rms[1, 1],
                 t_rms[0, 0],
                 t_rms[0, 1],
                 notes))
    
#with open(os.path.join(res_dir, folder+'_rms_notes.csv'), 'w') as fid:
#    fid.write('\n'.join(lines))                 

    
with open(res_fn[0:-4]+'rms__notes.csv', 'w') as fid:
    fid.write('\n'.join(lines))

