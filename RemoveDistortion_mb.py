# -*- coding: utf-8 -*-
"""
Created on Thu Dec 04 17:33:20 2014

@author: jpeacock-pr
"""

import mtpy.core.mt as mt
import os

#edi_path = r"c:\Users\jpeacock-pr\Google Drive\Mono_Basin\EDI_Files_dp"
edi_path = r"d:\Peacock\MTData\SanPabloBay\EDI_Files_dp"
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.find('.edi') > 0]
                
save_path = os.path.join(edi_path, 'DR')
if not os.path.isdir(save_path):
    os.mkdir(save_path)
    
log_fid = file(os.path.join(save_path, 'distortion.log'), 'w')

for edi in edi_list:
    mt_obj = mt.MT(edi)
    D, new_z = mt_obj.remove_distortion()
    # need to flip the arrays around for some reason
#    new_z.z = new_z.z[::-1, :, :]
#    new_z.zerr = new_z.zerr[::-1, :, :]
    mt_obj.Z = new_z
    mt_obj.write_edi_file(new_fn=os.path.join(save_path, 
                                              '{0}_dr.edi'.format(mt_obj.station)))
                                              
    log_fid.write('-'*50+'\n')
    log_fid.write('  Station -> {0}\n'.format(mt_obj.station))
    log_fid.write('{0}|{1: .2f} {2: .2f}|\n'.format(''*5, D[0,0], D[0,1]))
    log_fid.write('{0}|{1: .2f} {2: .2f}|\n'.format(''*5, D[1,0], D[1,1]))

log_fid.close()
                