# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 10:59:30 2017

@author: jpeacock
"""
import numpy as np
import mtpy.modeling.modem_new as modem

res_fn = r"c:\Users\jpeacock\Documents\iMush\modem_inv\imush_err05_cov04_NLCG_021.res"

res_obj = modem.Data()
res_obj.read_data_file(res_fn)

lines = []
for r_arr in res_obj.data_array:
    nz = np.nonzero(r_arr['z'])
    rms = r_arr['z'][nz].__abs__()/r_arr['z_err'][nz].real
    rms = rms.mean()
    if rms > 15.0:
        lines.append('{0:<8} = {1:<6.3f} ****'.format(r_arr['station'], rms))
    else:
        lines.append('{0:<8} = {1:<6.3f}'.format(r_arr['station'], rms))
    
with open(res_fn[0:-4]+'.rms', 'w') as fid:
    fid.write('\n'.join(lines))