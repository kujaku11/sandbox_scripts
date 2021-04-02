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

repeat_list = ["station,repeatability(%),repeatability_err(%)"]
for station in [3, 4, 13, 24, 30, 62, 70]:
    fn_01 = os.path.join(dir_path_01, "TNG-0{0:02}.edi".format(station))
    fn_02 = os.path.join(dir_path_02, "TNG-3{0:02}.edi".format(station))

    mt_01 = mt.MT()
    mt_01.read_mt_file(fn_01)

    mt_02 = mt.MT()
    mt_02.read_mt_file(fn_02)

    # get frequencies where no change is expected
    no_change = np.where(1.0 / mt_01.Z.freq < 2)

    # estimate a static shift in each mode
    ss_x = 1.0 / np.sqrt(
        np.median(np.abs(mt_02.Z.z[no_change, 0, 1] / mt_01.Z.z[no_change, 0, 1]))
    )
    ss_y = 1.0 / np.sqrt(
        np.median(np.abs(mt_02.Z.z[no_change, 1, 0] / mt_01.Z.z[no_change, 1, 0]))
    )

    mt_02.Z = mt_02.remove_static_shift(ss_x=ss_x, ss_y=ss_y)
    rpt = mtpt.ResidualPhaseTensor(mt_01.pt, mt_02.pt)

    repeat = np.median(np.abs(rpt.residual_pt.pt[no_change])) * 100
    repeat_err = np.median(np.abs(rpt.residual_pt.pt_err[no_change])) * 100

    print "TNG-0{0:02}, Repeatability is {1:.2f}% +/- {2:.2f}%".format(
        station, repeat, repeat_err
    )
    repeat_list.append(
        "TNG-0{0:02},{1:.2f}%,{2:.2f}".format(station, repeat, repeat_err)
    )

with open(
    r"c:\Users\jrpeacock\Documents\Test_Data\Tongario\repeatability_pt_det.txt", "w"
) as fid:
    fid.write("\n".join(repeat_list))
