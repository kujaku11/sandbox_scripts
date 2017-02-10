# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 15:04:22 2017

@author: jpeacock
"""

import os
import shutil
import mtpy.core.mt as mt

edi_path = r"c:\Users\jpeacock\Documents\iMush\iMush_edited_edi_files_JRP\Rotated_m16_deg"
sv_path = r"c:\Users\jpeacock\Documents\iMush\iMush_edited_edi_files_tipper_rot_geographic_north"

#s_list = ['1111', '0912', '0614', '0817', '0818', '0819', '0720', '1114',
#          '1215', '1313', '1016', '1115', '1312', '1314', '0916', '1217',
#          '1117', '1217', '1814', '1814', '1216', '1118', '1813', '1812',
#          '2111', '2110', '0810', '0811']

with open(r"c:\Users\jpeacock\Documents\iMush\imush_tippers_to_rotate.txt", 'r') as fid:
    s_list = fid.readlines()
    
s_list = [ss.strip() for ss in s_list]

for edi in os.listdir(edi_path):
    station = edi[:-4]
    if station in s_list:
        mt_obj = mt.MT(os.path.join(edi_path, edi))
        mt_obj.Tipper.rotate(180)
        mt_obj.write_edi_file(new_fn=os.path.join(sv_path, 
                                                  '{0}_tip_rot.edi'.format(station)))
        print 'rotated tipper for {0}'.format(edi)
        print '-'*40
    else:
        shutil.copy(os.path.join(edi_path, edi),
                    os.path.join(sv_path, edi))
#        print '  --> copied {0} to {1}'.format(os.path.join(edi_path, edi),
#                                                os.path.join(sv_path, edi))