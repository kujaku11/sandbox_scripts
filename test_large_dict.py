# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 13:05:33 2021

@author: jrpeacock
"""

from pathlib import Path
import numpy as np
from mtpy.core import mt
from datetime import datetime


edi_path = Path(r"c:\Users\jrpeacock\Documents\GitHub\mtpy\examples\data\ET_edi")
edi_list = list(edi_path.glob("*.edi"))

def make_mt_dict(edi_list):
    d = {}
    for edi in edi_list:
        mt_obj = mt.MT(edi)
        d[mt_obj.station] = mt_obj
    return d

def make_mt_dict_keys(edi_list):
    keys = [k.stem for k in edi_list]
    d = {}
    d.fromkeys(keys)
    for edi in edi_list:
        mt_obj = mt.MT(edi)
        d[mt_obj.station] = mt_obj
    return d

def append_to_dict(n):
    d = {}
    for ii in range(n):
        d[ii] = np.random.rand(4096)
    return d
        
def from_keys(n):
    keys = np.arange(n).tolist()
    d = {}
    d.fromkeys(keys)
    for k in keys:
        d[k] = np.random.rand(4096)
        
    return d

def iterate_mt_list(n):
    dt = []
    for edi in n:
        st = datetime.now()
        m = mt.MT(edi)
        et = datetime.now()
        diff = (et - st).total_seconds()
        m.logger.info(f"Took {diff}")
        dt.append(diff)
    return dt

# mt_dict = make_mt_dict(edi_list)
#m = mt.MT(edi_list[0])

df = iterate_mt_list(edi_list[0:100])




# if __name__ == "__main__":
#     d1 = append_to_dict(100)
#     d2 = from_keys(100)
        
    
    