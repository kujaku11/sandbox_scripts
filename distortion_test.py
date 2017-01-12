# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 12:11:47 2017

@author: jrpeacock
"""

import mtpy.core.mt as mt
import numpy as np
import copy
import os

import mtpy.imaging.mtplot as mtplot


edi_fn = r"c:\Users\jrpeacock\Documents\Test_Data\HalfSpaceSQC\par16ew.edi"

mt_obj = mt.MT(edi_fn)

D = np.array([[.8, -.1], 
              [.1, 1.0]])

dis_z = copy.deepcopy(mt_obj.Z)
dis_z.z = np.dot(dis_z.z, D)

edi_fn_d = edi_fn[0:-4]+'_d.edi'
edi_fn_dr = edi_fn[0:-4]+'_dr.edi'
if os.path.isfile(edi_fn_d) == True:
    os.remove(edi_fn_d)
    
if os.path.isfile(edi_fn_dr) == True:
    os.remove(edi_fn_dr)
mt_obj.write_edi_file(new_fn=edi_fn_d, new_Z=dis_z)

mt_obj_dis = mt.MT(edi_fn_d)
new_d, new_z = mt_obj_dis.remove_distortion(num_freq=3)

mt_obj_dis.write_edi_file(new_fn=edi_fn_dr, 
                          new_Z=new_z)

print('D = | {0:.2f} {1:.2f} |\n   | {2:.2f} {3:.2f} |'.format(D[0, 0],
                                                               D[0, 1],
                                                               D[1, 0],
                                                               D[1, 1]))

print('D = | {0:.2f} {1:.2f} |\n   | {2:.2f} {3:.2f} |'.format(new_d[0, 0],
                                                               new_d[0, 1],
                                                               new_d[1, 0],
                                                               new_d[1, 1]))

pmr = mtplot.plot_multiple_mt_responses(fn_list=[edi_fn, edi_fn_d, edi_fn_dr],
                                        plot_style='compare')