# -*- coding: utf-8 -*-
"""

Created on Tue Jul 28 17:26:16 2020

:author: Jared Peacock

:license: MIT

"""
from pathlib import Path

import pandas as pd
import numpy as np

mfn = r"c:\Users\peaco\Documents\MT\UM2020\TEM\Models\smooth\T00\_1_1.ml.mod"

with open(mfn, "r") as fid:
    lines = fid.readlines()

header = []
h_find = True
index = 0
while h_find:
    line = lines[index].strip().split()
    if len(line) == 1:
        h_find = False
    header.append(line)
    index += 1


n_layers, easting, northing, elev = [float(ii) for ii in lines[index].strip().split()]
n_layers = int(n_layers)

index += 1

model = {
    "resistivity": np.zeros(n_layers),
    "thickness": np.zeros(n_layers - 1),
    "depth": np.zeros(n_layers),
}

# read resistivity
for jj in range(n_layers):
    line = lines[index + jj].strip().split()
    model["resistivity"][jj] = line[0]

# read thickness
for jj in range(n_layers - 1):
    line = lines[index + n_layers + jj].strip().split()
    model["thickness"][jj] = line[0]

# read thickness
for jj in range(n_layers - 1):
    line = lines[index + 2 * n_layers - 1 + jj].strip().split()
    model["depth"][jj] = line[0]
model["depth"][-1] = 20000

df = pd.DataFrame(model["resistivity"], index=model["depth"])
