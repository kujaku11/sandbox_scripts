# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 15:50:19 2017

@author: jpeacock
"""
import os
import mtpy.core.mt as mt
import mtpy.imaging.plot_mt_response as pr
import pickle

# =============================================================================
# Inputs
# =============================================================================
dir_path = r"d:\Peacock\MTData\Camas\EDI_Files_birrp\Edited\Rotated_13_deg"
cfg_fn = r"d:\Peacock\MTData\Camas\EDI_Files_birrp\camas_birrp.cfg"
edi_path = r"d:\Peacock\MTData\Camas\EDI_Files_birrp\Edited\Rotated_13_deg"
sv_path = os.path.join(dir_path, r"Camas_EDI_Files_new")
plot_sv_path = os.path.join(dir_path, 'camas_plots')

with open(r"d:\Peacock\MTData\Camas\elevation.pkl", 'r') as fid:
    info_dict = pickle.load(fid)

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

# =============================================================================
# Make any directories needed
# =============================================================================
def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)
        
for d_path in [sv_path, plot_sv_path]:
    check_path(d_path)

# =============================================================================
# Get list of EDI's
# =============================================================================
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi')]

for edi in edi_list:

    mt_obj = mt.MT(edi)
    mt_obj.read_cfg_file(cfg_fn)
    mt_obj.elev = info_dict[mt_obj.station.lower()]['elev']
    mt_obj.FieldNotes.DataLogger.id = info_dict[mt_obj.station.lower()]['zen_id']
    #mt_obj.station = 'mb'+mt_obj.station
    for rm_key in rm_keys:
        try:
            mt_obj.Notes.info_dict.pop(rm_key)
        except KeyError:
            pass
#    p1 = pr.PlotMTResponse(z_object=mt_obj.Z, 
#                           t_object=mt_obj.Tipper,
#                           station=mt_obj.station,
#                           plot_num=2,
#                           phase_limits=(0, 109))
#    p1.save_plot(os.path.join(plot_sv_path, mt_obj.station+'.png'),
#                 fig_dpi=900)
#    pr.plt.close('all')
    
    mt_obj.write_mt_file(save_dir=sv_path)
#    mt_obj.write_mt_file(save_dir=xml_sv_path, file_type='xml')
    
    
    