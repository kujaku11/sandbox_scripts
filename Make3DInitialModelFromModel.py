# -*- coding: utf-8 -*-
"""
Created on Mon May 20 11:29:15 2013

@author: jpeacock-pr
"""

import mtpy1.modeling.ws3dtools as ws
import numpy as np
import os

mfn = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_AMT\Inv1_hs500_lake\MonoBasinAMT_smooth2__model.04"
itfn = r"c:\MinGW32-xy\Peacock\wsinv3d\MB_AMT\Inv5\init3d_3layers"

svpath = os.path.join(r"c:\MinGW32-xy\Peacock\wsinv3d\MB_AMT\Inv1_hs500_lake",
                      'init3d_testmodel')

#read in model
ns ,ew, zd, resarr, idict = ws.readModelFile(mfn)

#read in initial file
xg, yg, zg, reslsti, tstr, resmodel, xn, yn, zn = ws.readInit3D(itfn)

#make a list of values to find in model
reslst = np.array([1,10,50,100,500,1000], dtype=np.float)
resdict = dict([(res,ii) for ii,res in enumerate(reslst,1)])

#number of layers
nz = len(zd)

#make values in model resistivity array a value in reslst
resm = np.ones_like(resarr)
resm[np.where(resarr<reslst[0])] = resdict[reslst[0]]
resm[np.where(resarr)>reslst[-1]] = resdict[reslst[-1]]

for zz in range(resarr.shape[2]):
    for yy in range(resarr.shape[1]):
        for xx in range(resarr.shape[0]):
            for rr in range(len(reslst)-1):
                if resarr[xx,yy,zz]>=reslst[rr] and resarr[xx,yy,zz]<=reslst[rr+1]:
                    resm[xx,yy,zz] = resdict[reslst[rr]]
                    break
                elif resarr[xx,yy,zz]<=reslst[0]:
                    resm[xx,yy,zz] = resdict[reslst[0]]
                    break
                elif resarr[xx,yy,zz]>=reslst[-1]:
                    resm[xx,yy,zz] = resdict[reslst[-1]]
                    break

#for zz in range(1):
#    for yy in range(resarr.shape[1]):
#        for xx in range(resarr.shape[0]):
#
#            for rr in range(len(reslst)-1):
#                if resarr[xx,yy,zz]>=reslst[rr] and resarr[xx,yy,zz]<=reslst[rr+1]:
#                    resm[xx,yy,zz] = resdict[reslst[rr]]
#                    break
#                elif resarr[xx,yy,zz]<=reslst[0]:
#                    resm[xx,yy,zz] = resdict[reslst[0]]
#                    print '00---{0:.1f}---{1}'.format(resarr[xx,yy,zz],
#                                                      resdict[reslst[0]])
#                    break
#                elif resarr[xx,yy,zz]>=reslst[-1]:
#                    resm[xx,yy,zz] = resdict[reslst[-1]]
#                    print '11---{0:.1f}---{1}'.format(resarr[xx,yy,zz],
#                                                      resdict[reslst[-1]])
#                    break
                
#write new initial file
initfn = ws.writeInit3DFile(xn, yn, zn, svpath, reslst=list(reslst), 
                            title='Initial Model for WSINV3D',
                            resmodel=resm[::-1,:,:])
                          
print '-'*25
print '     Resistivity Values'
for key in np.sort(resdict.keys()):
    print resdict[key], key
print '-'*25

print '-'*25
print '     Depth Values'
for ii,dd in enumerate(zg,1):
    print ii, dd
print '-'*25

    


