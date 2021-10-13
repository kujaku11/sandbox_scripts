# -*- coding: utf-8 -*-
"""
Created on Tue Sep 06 12:08:48 2016

@author: jpeacock-pr
"""

import mtpy.imaging.mtplot as mtplot
import os

edi_path = r"c:\MT\MB\EDI_Files_ga"
edi_list = [
    os.path.join(edi_path, edi) for edi in os.listdir(edi_path) if edi.endswith(".edi")
]

save_path = os.path.join(edi_path, "response_plots")
if not os.path.exists(save_path):
    os.mkdir(save_path)

for edi_fn in edi_list:
    rp = mtplot.plot_mt_response(fn=edi_fn, plot_num=2, plot_tipper="yri", plot_pt="y")
    rp.save_plot(
        os.path.join(save_path, "{0}.png".format(rp._mt.station)),
        file_format="png",
        fig_dpi=900,
    )
