# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 12:24:21 2014

@author: jpeacock-pr
"""

import mtpy.modeling.occam2d_rewrite as oc
import os
import numpy as np

xpad = 7

mfn_list = [r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\Line1\Inv3_TMPhase_tip\test12.iter",
            r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\Line2\Inv3_TMPhase_tip\test12.iter",
            r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\Line6\Inv2_TMphase_tip\test11.iter",
            r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\Line9\Inv1_TMPhase\Line9_Inv1_TMPhase_SM2_08.iter"]
 
dfn_list = [r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\Line1\Inv3_TMPhase_tip\OccamDataFile.dat",
            r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\Line2\Inv3_TMPhase_tip\OccamDataFile.dat",
            r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\Line6\Inv2_TMphase_tip\OccamDataFile.dat",
            r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\Line9\Inv1_TMPhase\OccamDataFile.dat"]

x0_list = [317046., 317315., 315779., 319813] 
y0_list = [4199329., 4194564., 4189958., 4187957.]

header_line = '{0:^15}{1:^15}{2:^15}{3:^15}\n'.format('east', 'north', 
                                                     'depth', 'resistivity')
                                                     
lines = [header_line]

for mfn, dfn, x0, y0 in zip(mfn_list, dfn_list, x0_list, y0_list):
    ocm = oc.Model()
    ocm.iter_fn = mfn
    ocm.build_model()
    
    ocd = oc.Data()
    ocd.read_data_file(dfn)
    
    easting = (ocm.plot_x+x0)*np.cos(np.deg2rad(5.))
    for ii, east in enumerate(easting):
        for zz, depth in enumerate(ocm.plot_z):
            lines.append('{0:>15.1f}{1:>15.1f}{2:>15.1f}{3:>15.1f}\n'.format(
                         east, y0, depth, 10**ocm.res_model[zz, ii]))
        
ofid = file(r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\2DStartingModel.txt", 
            'w')
ofid.writelines(lines)
ofid.close()


