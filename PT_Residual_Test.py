# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 11:36:26 2014

@author: jpeacock-pr
"""

import mtpy.imaging.mtplot as mtplot
import os

line_dir = "ew"

edipath_i = r"g:\Peacock\PHD\Geothermal\Paralana\EDIFilesInjection\EDIfiles\CFA\DR"
edipath_b = r"g:\Peacock\PHD\Geothermal\Paralana\EDIFilesBaseSurvey\CFA\SS\DR"

if line_dir == "ew":
    pslst = ["pb{0:02}".format(ii) for ii in range(44, 33, -1)] + [
        "pb{0:02}".format(ii) for ii in range(23, 34)
    ]
    pslst.remove("pb31")
    pslst.remove("pb34")

elif line_dir == "ns":
    pslst = (
        ["pb{0:02}".format(ii) for ii in range(22, 11, -1)]
        + ["pb0{0:02}".format(ii) for ii in range(1, 10)]
        + ["pb10", "pb11"]
    )
    pslst.remove("pb05")
    pslst.remove("pb06")
    pslst.remove("pb12")

inj_list = [os.path.join(edipath_i, "{0}.edi".format(ss)) for ss in pslst]
base_list = [os.path.join(edipath_b, "{0}.edi".format(ss)) for ss in pslst]

ptr = mtplot.plot_residual_pt_ps(base_list, inj_list)
