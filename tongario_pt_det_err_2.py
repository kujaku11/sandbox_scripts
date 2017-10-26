# -*- coding: utf-8 -*-
"""
Created on Fri Oct 06 12:51:50 2017

@author: jrpeacock
"""

import os
import mtpy.core.mt as mt
import numpy as np
import mtpy.analysis.pt as mtpt


dir_path_01 = r"c:\Users\jrpeacock\Documents\Test_Data\Tongario\original"
dir_path_02 = r"c:\Users\jrpeacock\Documents\Test_Data\Tongario\repeat"

line_list = []
for station in ([3]): #, 4, 13, 24, 30, 62, 70]):
    fn_01 = os.path.join(dir_path_01, 'TNG-0{0:02}.edi'.format(station))
    fn_02 = os.path.join(dir_path_02, 'TNG-3{0:02}.edi'.format(station))
    
    mt_01 = mt.MT()
    mt_01.read_mt_file(fn_01)
    
    mt_02 = mt.MT()
    mt_02.read_mt_file(fn_02)
    
    # get frequencies where no change is expected
    no_change = np.where(1./mt_01.Z.freq < 2)

    rpt = mtpt.ResidualPhaseTensor(mt_01.pt, mt_02.pt)
    line_list.append('-'*72)
    line_list.append('# *** TNG-0{0:02} ***'.format(station))
    line_list.append('-'*72)
    for ff, pt_det in zip(rpt.freq, rpt.residual_pt.pt_err):
        line_list.append('{0:.6f},{1:.3f}'.format(1./ff, abs(np.median(pt_det)*100)))

#with open(r"c:\Users\jrpeacock\Documents\Test_Data\Tongario\pt_det_err.txt", 'w') as fid:
#    fid.write('\n'.join(line_list))
    
    