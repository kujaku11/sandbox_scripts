# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 15:01:00 2020

@author: jpeacock
"""
from pathlib import Path
from mtpy.core import mt
from mtpy.core import z
import numpy as np

fn_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\LV\Inversions\MonoLake\mono_lake_response_files")
f_list = [63.0120, 37.9939, 24.4978, 15.4991, 10.0000, 5.9999, 3.8751, 2.5000,
          1.5000, 0.9687, 0.6250, 0.3750, 0.2422, 0.1562, 0.0937, 0.0605,
          0.0391, 0.0234, 0.0151, 0.0098, 0.0059, 0.0038, 0.0024, 0.0015,
          0.0009, 0.0006, 0.0004, 0.0002]
def read_txt(text_fn):
    index_dict = {0:(0, 0), 1:(0, 1), 2:(1, 0), 3:(1, 1),
                  4:(0, 0), 5:(0, 1), 6:(1, 0), 7:(1, 1)}
    if not isinstance(text_fn, Path):
        text_fn = Path(text_fn)
        
    lines = text_fn.read_text().split('\n')
    nf = len(lines) - 1
    z = np.zeros((nf, 2, 2,), dtype=np.complex)
    err = np.zeros((nf, 2, 2), dtype=np.float)
    
    for mm, line in enumerate(lines):
        z_list = line.split()
        for ii, zz in enumerate(z_list):
            jj, kk = index_dict[ii]
            try:
                zr, zi = zz.split('+')
                zi = zi.replace('i', '')
            except ValueError:
                zr = zz
                zi = 0
            if ii < 4:
                z[mm, jj, kk] = float(zr) - 1j * float(zi)
            else:
                err[mm, jj, kk] = np.sqrt(np.abs(float(zr) + 1j * float(zi)))
                
    z[:, 1, 0] *= -1
    z[:, 0, 1] *= 796
    z[:, 1, 0] *= 796
                
    return z, err
            
for txt_fn in fn_path.glob('*.txt'):
    # if 's22' not in txt_fn.name:
    #     continue
    zmm_fn = txt_fn.with_suffix('.zmm')
    if zmm_fn.exists():
        m_obj = mt.MT(zmm_fn)
        new_z, new_err = read_txt(txt_fn)
        m_obj.Z = z.Z(new_z, new_err, np.array(f_list))
        m_obj.write_mt_file(fn_basename='{0}_uc'.format(m_obj.station))
    else:
        print('ERROR: No zmm file {0}'.format(zmm_fn))
    
    