# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 15:06:46 2019

@author: jpeacock
"""

import numpy as np

fn = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\gis\gv_topo.txt"
resample = 6

with open(fn, 'r') as fid:
    nx = int(fid.readline().split()[1].strip())
    ny = int(fid.readline().split()[1].strip())
    x = float(fid.readline().split()[1].strip())
    y = float(fid.readline().split()[1].strip())
    cell = float(fid.readline().split()[1].strip())
    nil = float(fid.readline().split()[1].strip())
    topo = np.zeros((nx/resample, ny/resample), dtype=np.float)

    for ii in range(ny/resample):
        try:
            line = fid.readline()
            topo[:, ii] = np.array(line.strip().split(),
                                   dtype=np.float)[::resample]

        except ValueError as error:
            raise ValueError(error)
            
        for jj in range(resample-1):
            fid.readline()
            
topo[np.where(topo == -9999)] = 0
with open(fn[0:-4]+'_150m.txt', 'w') as nfid:
    header = []
    header.append('{0:14}{1:.0f}'.format('ncols', topo.shape[0]))
    header.append('{0:14}{1:.0f}'.format('nrows', topo.shape[1]))
    header.append('{0:14}{1:.11f}'.format('xllcorner', x))
    header.append('{0:14}{1:.11f}'.format('yllcorner', y))
    header.append('{0:14}{1:.11f}'.format('cellsize', cell*resample))
    header.append('{0:14}{1:.0f}'.format('NODATA_value', nil))
    nfid.write('\n'.join(header))
    nfid.write('\n')
    for kk in range(topo.shape[1]):
        out = np.char.mod('%.6g', topo[:, kk])
        nfid.write(' '.join(out))
        nfid.write('\n')
    

            
    
    


