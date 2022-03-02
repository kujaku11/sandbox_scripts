# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 11:54:32 2022

@author: jpeacock
"""

import h5py

f = h5py.File(r"h5_transfer_function_container.h5", "a")

tf = f.create_dataset("tf", (20, 3, 2)) 

tf.dims[0].label = "period"
tf.dims[1].label = "output"
tf.dims[2].label = "input"

f["output"] = ["ex", "ey", "hz"]
f["input"] = ["hx", "hy"]
f["ex"] = 0
f["ey"] = 1
f["hx"] = 2
f["hy"] = 0
f["hz"] = 1

f["ex"].make_scale("ex")
f["ey"].make_scale("ey")
f["hx"].make_scale("hx")
f["hy"].make_scale("hy")
f["hz"].make_scale("hz")


tf.dims[1].attach_scale(f["ex"])
tf.dims[1].attach_scale(f["ey"])
tf.dims[1].attach_scale(f["hz"])

tf.dims[2].attach_scale(f["hx"])
tf.dims[2].attach_scale(f["hy"])

