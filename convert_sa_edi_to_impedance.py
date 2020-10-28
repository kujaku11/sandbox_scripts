# -*- coding: utf-8 -*-
"""
Created on Tue Mar 08 11:30:24 2016

@author: jpeacock
"""

import mtpy.core.mt as mt

# import mtpy.core.edi as mtedi
import os

edi_path = r"c:\Users\jpeacock\Documents\SaudiArabia\edi_files_fixed_lon"
save_path = r"c:\Users\jpeacock\Documents\SaudiArabia\edi_files_z"
plot_path = r"c:\Users\jpeacock\Documents\SaudiArabia\resp_plots"

edi_list = [
    os.path.join(edi_path, edi) for edi in os.listdir(edi_path) if edi[-4:] == ".edi"
]

for edi in edi_list[-9:]:
    new_edi_fn = os.path.join(save_path, os.path.basename(edi))
    mt_obj = mt.MT(fn=edi, data_type="spectra")
    mt_obj.write_edi_file(new_fn=new_edi_fn)

    mt_obj = mt.MT(new_edi_fn)
    pr = mt_obj.plot_mt_response(plot_pt="y", plot_tipper="yri")
    pr.save_plot(
        os.path.join(plot_path, os.path.basename(new_edi_fn)[:-4] + ".png"), fig_dpi=900
    )
