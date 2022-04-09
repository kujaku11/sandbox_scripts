# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 18:12:22 2018

@author: jpeacock-pr
"""

import os

comp = "hz"
swap_comp = "hx"

c_dir = {"hx": "ch1", "hy": "ch2", "hz": "ch3", "ex": "ch4", "ey": "ch5"}

z3d_dir = r"c:\MT\SAGE_2018\s3"

fn_list = [
    os.path.join(z3d_dir, fn)
    for fn in os.listdir(z3d_dir)
    if c_dir[comp] in fn.lower() and fn.endswith(".z3d")
]
for fn in fn_list:
    with open(fn, "rb") as fid:
        fn_str = fid.read()
        fn_str = fn_str.replace(comp.capitalize(), swap_comp.capitalize())
    with open(fn[:-4] + "_swap.z3d", "wb") as fid:
        fid.write(fn_str)
