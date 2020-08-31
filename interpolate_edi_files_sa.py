
# coding: utf-8

# ## Interpolate a list of .edi files onto the same period range


import os
import mtpy.core.mt as mt
import numpy as np

edi_path = r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\GabbsValley\EDI_Files_birrp\Edited"
edi_list = [os.path.join(edi_path, edi_fn) for edi_fn in os.listdir(edi_path)
             if edi_fn.endswith('.edi')]

save_path = os.path.join(edi_path, 'Interpolated')
if not os.path.isdir(save_path):
    os.mkdir(save_path)

# make a new frequency list to interpolate on to [1000 Hz - 1000 sec]
interp_freq = np.logspace(np.log10(1./1.031E-3), np.log10(1./2048), num=48)

for edi_fn in edi_list:
    mt_obj = mt.MT(edi_fn)
    new_f = interp_freq[np.where((interp_freq >= mt_obj.Z.freq.min()) & 
                                 (interp_freq <= mt_obj.Z.freq.max()))]
    new_z_obj, new_t_obj = mt_obj.interpolate(new_f)
    new_z_obj.rotation_angle = np.repeat(mt_obj.Z.rotation_angle[0], 
                                         new_f.size)
    new_t_obj.rotation_angle = np.repeat(mt_obj.Tipper.rotation_angle[0],
                                         new_f.size)
    mt_obj.write_mt_file(save_dir=os.path.join(edi_path, 'Interpolated'),
                         new_Z_obj=new_z_obj, new_Tipper_obj=new_t_obj)




