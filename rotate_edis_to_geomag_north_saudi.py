# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 17:42:06 2017

@author: jpeacock
"""
import os
import mtpy.core.mt as mt

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\EDI_Files\Edited_01"

edi_list = [os.path.join(edi_path, ss) for ss in os.listdir(edi_path)
            if ss.endswith('.edi')]

sv_path = os.path.join(edi_path, 'geomag_north')               
if not os.path.exists(sv_path):
    os.mkdir(sv_path)
    print 'Made directory {0}'.format(sv_path)

for edi in edi_list:
    mt_obj = mt.MT(fn=edi)
    if mt_obj.Z.rotation_angle.mean() == -34.:
        mt_obj.rotation_angle = 34
    elif mt_obj.Z.rotation_angle.mean() == -30:
        mt_obj.rotation_angle = 30
    elif mt_obj.Z.rotation_angle.mean() == 0.0:
        mt_obj.rotation_angle = -30
        
    
    mt_obj.rotation_angle = 0.0
    mt_obj.write_edi_file(new_fn=os.path.join(sv_path, os.path.basename(edi)))                