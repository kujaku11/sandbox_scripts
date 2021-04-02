# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 12:25:13 2020

:author: Jared Peacock

:license: MIT

"""

from pathlib import Path
import numpy as np

fn = Path(r"c:\Users\jpeacock\Downloads\st_z05_t02_c035_102.out")

with open(fn, "r") as fid:
    lines = fid.readlines()

nx, ny, nz = lines[0]
# x, y, z = []
# res = []
# header = []

# for line in lines:
