# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 11:38:26 2018

@author: jpeacock
"""

import mtpy.core.mt as mt
import numpy as np

station = 'med620'

lp_fn = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\GeomagneticNorth_original_lp\{0}.edi".format(station)
bb_fn = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\GeomagneticNorth_original\{0}.edi".format(station)
cfg_fn = r"C:\Users\jpeacock\Documents\SaudiArabia\sa_edi_combined.cfg"

lp_obj = mt.MT(lp_fn)
bb_obj = mt.MT(bb_fn)

f_merge = 1./42

#### --> Apply static shift
# > 1 makes the curve go down
# < 1 makes the curve go up
ss_x = .85
ss_y = 1.0

### --> apply static shift to broad band cause lp is assumed to be more 
###     accurate
bb_z_obj = bb_obj.remove_static_shift(ss_x=ss_x, ss_y=ss_y)

### --> merge Z
lp_f = lp_obj.Z.freq[np.where(lp_obj.Z.freq <= f_merge)]
lp_z = lp_obj.Z.z[np.where(lp_obj.Z.freq <= f_merge)]
lp_z_err = lp_obj.Z.z_err[np.where(lp_obj.Z.freq <= f_merge)] 

bb_f = bb_z_obj.freq[np.where(bb_z_obj.freq >= f_merge)]
bb_z = bb_z_obj.z[np.where(bb_z_obj.freq >= f_merge)]
bb_z_err = bb_z_obj.z_err[np.where(bb_z_obj.freq >= f_merge)]

merged_z_obj = mt.MTz.Z(z_array=np.append(bb_z, lp_z, axis=0),
                        z_err_array=np.append(bb_z_err, lp_z_err, axis=0),
                        freq=np.append(bb_f, lp_f, axis=0))

### --> merge Tipper
lp_f = lp_obj.Tipper.freq[np.where(lp_obj.Tipper.freq <= f_merge)]
lp_t = lp_obj.Tipper.tipper[np.where(lp_obj.Tipper.freq <= f_merge)]
lp_t_err = lp_obj.Tipper.tipper_err[np.where(lp_obj.Tipper.freq <= f_merge)] 

bb_f = bb_obj.Tipper.freq[np.where(bb_obj.Tipper.freq >= f_merge)]
bb_t = bb_obj.Tipper.tipper[np.where(bb_obj.Tipper.freq >= f_merge)]
bb_t_err = bb_obj.Tipper.tipper_err[np.where(bb_obj.Tipper.freq >= f_merge)]

merged_t_obj = mt.MTz.Tipper(tipper_array=np.append(bb_t, lp_t, axis=0),
                             tipper_err_array=np.append(bb_t_err, lp_t_err, axis=0),
                             freq=np.append(bb_f, lp_f, axis=0))

### --> write new file
lp_obj.read_cfg_file(cfg_fn)
new_fn = lp_obj.write_mt_file(save_dir=r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\GeomagneticNorth_original_combined",
                              fn_basename='{0}_c.edi'.format(station),
                              new_Z_obj=merged_z_obj,
                              new_Tipper_obj=merged_t_obj)

mt_obj = mt.MT(new_fn)
pr = mt_obj.plot_mt_response(plot_num=2)