#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 10:31:12 2019

@author: jpeacock
"""

import os
import glob
from mtpy.imaging import mtplot

edi_path_good = r"/mnt/hgfs/MTData/SAGE_2019/EDI_Files_birrp/Edited/GeographicNorth/final_edi"
edi_path_old = r"/mnt/hgfs/MTData/SAGE_2019/EDI_Files_birrp_field"
edi_path_sage = r"/mnt/hgfs/jpeacock/OneDrive - DOI/SAGE/EDI_Files"

match_dict = {'SG1901':['jmz017', 'jmz010'],
              'SG1902':['jmz018'],
              'SG1903':['jmz005'],
              'SG1904':['jmz027', 'jmz026'],
              'SG1905':['jmz020'],
              'SG1906':['BND009']}

edi_list_good = list(sorted(glob.glob('{0}/*.edi'.format(edi_path_good))))
edi_list_old = list(sorted(glob.glob('{0}/*.edi'.format(edi_path_old))))

for edi_good in edi_list_good:
    station = os.path.basename(edi_good)[0:-4] 
    if station in list(match_dict.keys()):
        edi_add = [os.path.join(edi_path_sage, m_fn+'.edi') for m_fn in match_dict[station]]
        edi_list = edi_add + [edi_good]

    else:
        edi_list = [edi_good]
    ptm = mtplot.plot_multiple_mt_responses(fn_list=edi_list,
                                            plot_tipper='yr',
                                            plot_style='compare',
                                            tipper_limits=(-.3, .3))
    ptm.fig.savefig(os.path.join(edi_path_good, station+'compare.png'), dpi=900)




