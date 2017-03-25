# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 15:25:26 2016

@author: jpeacock
"""

import mtpy.modeling.modem_new as modem
import os
import mtpy.utils.latlongutmconversion as utm2ll
import numpy as np

mfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_final_err05_cov04_NLCG_040.rho"
dfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_modem_data_ef05.dat"

#mfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\modem_inv\mshs_err03_cov03_NLCG_070.rho"
#dfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSHS\modem_inv\mshs_modem_data_err10_old.dat"

#mfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\modem_inv\mb_rot_err03_tip02_cov03_NLCG_016.rho"
#dfn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MB\modem_inv\mb_modem_data_err05_rot_edit.dat"

save_root = 'mshn'

#--> read model file
mod_obj = modem.Model()
mod_obj.read_model_file(mfn)

#--> read data file
d_obj = modem.Data()
d_obj.read_data_file(dfn)

#--> get center position
model_center = d_obj.center_position
#c_zone, c_east, c_north = utm2ll.LLtoUTM(23, model_center[0], model_center[1])
c_zone, c_east, c_north = (0, 0, 0)

#--> set padding
east_pad = mod_obj.pad_east+4
north_pad = mod_obj.pad_north+4
z_pad = np.where(mod_obj.grid_z > 50000)[0][0]

#--> write model xyz file
lines = ['# Resistivity model for {0}'.format(save_root.upper())]
lines.append('# Model Center(lat, lon) WGS84: {0:>+.6f}, {1:>+.6f}'.format(model_center[0], 
                                                      model_center[1]))
lines.append('#{0:>12}{1:>12}{2:>12}{3:>12}'.format('Northing (m)',
                                                              'Easting (m)',
                                                              'Depth (m)',
                                                              'Log10(res (Ohm-m))'))
#for kk, zz in enumerate(mod_obj.grid_z[0:z_pad]):
#    for jj, yy in enumerate(mod_obj.grid_east[east_pad:-east_pad]):
#        for ii, xx in enumerate(mod_obj.grid_north[north_pad:-north_pad]):
for kk, zz in enumerate(mod_obj.grid_z):
    for jj, yy in enumerate(mod_obj.grid_east):
        for ii, xx in enumerate(mod_obj.grid_north):
            
            lines.append('{0:>12.1f}{1:12.1f}{2:12.1f}{3:12.2f}'.format(
                          xx+c_north, 
                          yy+c_east, 
                          zz, 
                          np.log10(mod_obj.res_model[ii, jj, kk])))

save_fn = os.path.join(os.path.dirname(mfn), '{0}_resistivity_rel_coord.xyz'.format(save_root))
with open(save_fn, 'w') as fid:
    fid.write('\n'.join(lines))
    
print 'Wrote file {0}'.format(save_fn)
#--> write data xyz file
d_lines = ['{0:<8}{1:>14}{2:>14}{3:>14}{4:>14}{5:>14}'.format('station', 'rel_east', 'rel_north', 'elevation', 'lat', 'lon')]
for s_arr in d_obj.station_locations: 
    d_lines.append('{0:<8}{1:>14.2f}{2:>14.2f}{3:>14.2f}{4:>14.2f}{5:>14.2f}'.format(
                    s_arr['station'], 
                    s_arr['rel_east'],
                    s_arr['rel_north'],
                    s_arr['elev'],
                    s_arr['lat'],
                    s_arr['lon']))
                    
save_fn = os.path.join(os.path.dirname(mfn), '{0}_stations_rel_coord.xyz'.format(save_root))
with open(save_fn, 'w') as fid:
    fid.write('\n'.join(d_lines))
print 'Wrote file {0}'.format(save_fn)

    