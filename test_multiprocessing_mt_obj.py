# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 12:07:11 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from collections import OrderedDict
import multiprocessing as mp
from mtpy import MT
import mt_metadata

# =============================================================================

fn_list = [
    value for key, value in mt_metadata.__dict__.items() if key.startswith("TF")
]


def mt_read(fn):
    mt_obj = MT()
    mt_obj.read(fn)
    return mt_obj


def main():
    pool = mp.Pool()

    res = pool.map(mt_read, fn_list)
    pool.close()
    pool.join()
    return res


if __name__ == "__main__":
    res = main()
