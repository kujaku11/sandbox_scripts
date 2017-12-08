# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 15:50:19 2017

@author: jpeacock
"""
import os
import mtpy.core.mt as mt

cfg_fn = r"D:\Peacock\MTData\EDI_Folders\MSH_EDI_Files\msh_zonge.cfg"

edi_path = r"d:\Peacock\MTData\EDI_Folders\MSH_EDI_Files"

edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi')]

# keys to remove from file
rm_keys = ['b_instrument_amplification', 
           'b_instrument_type',
           'b_logger_gain',
           'b_logger_type',
           'b_xaxis_azimuth',
           'b_yaxis_azimuth',
           'box',
           'e_instrument_amplification',
           'e_instrument_type',
           'e_logger_gain',
           'e_logger_type',
           'e_xaxis_azimuth',
           'e_xaxis_length',
           'e_yaxis_azimuth',
           'e_yaxis_length',
           'edifile_generated_with',
           'hx',
           'hy',
           'hz',
           'save_path',
           'sampling_interval',
           'notes']

for edi in edi_list:
    mt_obj = mt.MT(edi)
    mt_obj.read_cfg_file(cfg_fn)
    for rm_key in rm_keys:
        mt_obj.Notes.info_dict.pop(rm_key)
        
    mt_obj.write_mt_file(save_dir=r"d:\Peacock\MTData\EDI_Folders\MSHN_EDI_Files")
    