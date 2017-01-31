# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 15:04:22 2017

@author: jpeacock
"""

import os
import mtpy.core.mt as mt

edi_path = r"c:\Users\jpeacock\Documents\iMush\iMush_edited_edi_files_JRP\Rotated_m16_deg"


s_list = ['1111', '0912', '0614', '0817', '0818', '0819', '0720', '1114',
          '1215', '1313', '1016', '1115', '1312', '1314', '0916', '1217',
          '1117', '1217', '1814', '1814', '1216', '1118', '1813', '1812',
          '2111', '2110', '0810', '0811']

for station in sorted(s_list):
    mt_obj = mt.MT(os.path.join(edi_path, '{0}.edi'.format(station)))
    mt_obj.Tipper.rotate(180)
    mt_obj.write_edi_file(new_fn=os.path.join(edi_path, 
                                              '{0}_tip_rot.edi'.format(station)))
