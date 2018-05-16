# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 15:50:19 2017

@author: jpeacock
"""
import os
import mtpy.core.mt as mt
import mtpy.imaging.plot_mt_response as pr

#dir_path = r"c:\Users\jrpeacock\Documents\EDI_Folders"
dir_path = r"d:\Peacock\MTData\EDI_Folders"
cfg_fn = os.path.join(dir_path, r"MSH_EDI_Files\msh_birrp.cfg")
edi_path = os.path.join(dir_path, r"MB_EDI_Files")
sv_path = os.path.join(dir_path, r"MB_EDI_Files_new")
xml_sv_path = os.path.join(dir_path, "MB_XML_Files")
plot_sv_path = os.path.join(dir_path, 'MB_plots')

def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)
        
for d_path in [sv_path, xml_sv_path, plot_sv_path]:
    check_path(d_path)

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
    mt_obj.station = 'mb'+mt_obj.station
    for rm_key in rm_keys:
        try:
            mt_obj.Notes.info_dict.pop(rm_key)
        except KeyError:
            pass
    p1 = pr.PlotMTResponse(z_object=mt_obj.Z, 
                           t_object=mt_obj.Tipper,
                           station=mt_obj.station,
                           plot_num=2,
                           phase_limits=(0, 109))
    p1.save_plot(os.path.join(plot_sv_path, mt_obj.station+'.png'),
                 fig_dpi=900)
    pr.plt.close('all')
    
    mt_obj.write_mt_file(save_dir=sv_path)
    mt_obj.write_mt_file(save_dir=xml_sv_path, file_type='xml')
    
    
    