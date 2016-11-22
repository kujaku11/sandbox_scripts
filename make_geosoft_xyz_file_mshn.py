# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 15:25:26 2016

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os
import mtpy.utils.latlongutmconversion as utm2ll
import numpy as np

#mfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_err05_cov03_NLCG_063.rho"
#dfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_modem_tip_data_ef03.dat"

mfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\modem_inv\mshs_err03_cov03_NLCG_070.rho"
dfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\modem_inv\mshs_modem_data_err10_old.dat"

save_root = 'mshs'

#--> read model file
mod_obj = modem.Model()
mod_obj.read_model_file(mfn)

#--> read data file
d_obj = modem.Data()
d_obj.read_data_file(dfn)

#--> get center position
model_center = d_obj.center_position
c_zone, c_east, c_north = utm2ll.LLtoUTM(23, model_center[0], model_center[1])

#--> set padding
east_pad = mod_obj.pad_east+4
north_pad = mod_obj.pad_north+4
z_pad = np.where(mod_obj.grid_z > 20000)[0][0]

#--> write model xyz file
lines = []
for kk, zz in enumerate(mod_obj.grid_z[0:z_pad]):
    for jj, yy in enumerate(mod_obj.grid_east[east_pad:-east_pad]):
        for ii, xx in enumerate(mod_obj.grid_north[north_pad:-north_pad]):
            
            lines.append('{0:>12.1f}{1:12.1f}{2:12.1f}{3:12.2f}'.format(
                          xx+c_north, 
                          yy+c_east, 
                          zz, 
                          mod_obj.res_model[ii, jj, kk]))

save_fn = os.path.join(os.path.dirname(mfn), '{0}_resistivity.xyz'.format(save_root))
with open(save_fn, 'w') as fid:
    fid.write('\n'.join(lines))
    
print 'Wrote file {0}'.format(save_fn)
#--> write data xyz file
d_lines = ['{0:<8}{1:>14}{2:>14}{3:>14}'.format('station', 'east', 'north', 'elevation')]
for s_arr in d_obj.station_locations: 
    d_lines.append('{0:<8}{1:>14.2f}{2:>14.2f}{3:>14.2f}'.format(
                    s_arr['station'], 
                    s_arr['east'],
                    s_arr['north'],
                    s_arr['elev']))
                    
save_fn = os.path.join(os.path.dirname(mfn), '{0}_stations.xyz'.format(save_root))
with open(save_fn, 'w') as fid:
    fid.write('\n'.join(d_lines))
print 'Wrote file {0}'.format(save_fn)

    