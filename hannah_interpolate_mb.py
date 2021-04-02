# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 11:31:30 2020

@author: jpeacock
"""

import os
from mtpy.modeling import occam1d
from mtpy.core import mt

edi_dir = r"c:\Users\jpeacock\OneDrive - DOI\EDI_FILES"
occam_fn = r"c:\Users\jpeacock\Downloads\Occam1D.data"
save_dir = r"c:\Users\jpeacock\Downloads"

# station_list = [59, 129, 46, 54, 125, 72, 73, 126, 74, 90, 174, 211, 172]

station_list = [130, 41, 36, 70, 153, 172, 89]

edi_list = [os.path.join(edi_dir, "mb{0:03}.edi".format(ii)) for ii in station_list]

od = occam1d.Data()
od.read_data_file(occam_fn)

for edi_fn in edi_list:
    mt_obj = mt.MT(edi_fn)
    new_z, new_t = mt_obj.interpolate(od.freq, bounds_error=False)
    mt_obj.write_mt_file(save_dir=save_dir, new_Z_obj=new_z, new_Tipper_obj=new_t)
