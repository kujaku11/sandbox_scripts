# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 15:28:51 2017

@author: jpeacock-pr
"""

import mtpy.usgs.zen_processing as zp
import mtpy.imaging.plotnresponses as pmr
import mtpy.imaging.plotresponse as pr


station = "mb510"

edi_fn_list = [
    r"c:\MT\MB\{0}\TS\BF\4096\{0}.edi".format(station),
    r"c:\MT\MB\{0}\TS\BF\256\{0}.edi".format(station),
    r"c:\MT\MB\{0}\TS\BF\16\{0}.edi".format(station),
]

p1 = pmr.PlotMultipleResponses(fn_list=edi_fn_list, plot_style="compare")

k = zp.Z3D_to_edi()
k.station_dir = r"c:\MT\MB\{0}\TS".format(station)
nedi = k.combine_edi_files(
    edi_fn_list, sr_dict={4096: (1000.0, 0.1), 256: (0.11, 0.12), 16: (0.12, 0.0001)}
)

p2 = pr.PlotResponse(fn=nedi, plot_tipper="yri", fig_num=3)
