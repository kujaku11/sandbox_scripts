# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 15:41:48 2013

@author: jpeacock
"""

import mtpy.core.z as Z
import os
import numpy as np
import mtpy.utils.latlongutmconversion as utm2ll
import scipy.signal as sps

amtline='B'

if amtline=='D':
    edipath=r"h:\Peacock\USGSPostDoc\MonoBasin\MonoBasin_AMT\2012\MBD_processed"
    metafn=r"h:\Peacock\USGSPostDoc\MonoBasin\MonoBasin_AMT\2012\MBD.txt"
    edistem='ZMBD0'
    nlines=23

elif amtline=='C':
    edipath=r"h:\Peacock\USGSPostDoc\MonoBasin\MonoBasin_AMT\2012\MBC_processed"
    metafn=r"h:\Peacock\USGSPostDoc\MonoBasin\MonoBasin_AMT\2012\MBC.txt"
    edistem='ZMBC0'
    nlines=17
    
elif amtline=='A':
    edipath=r"h:\Peacock\USGSPostDoc\MonoBasin\MonoBasin_AMT\2011\MBA_NEW"
    metafn=r"h:\Peacock\USGSPostDoc\MonoBasin\MonoBasin_AMT\2011\MBA2.txt"    
    edistem='ZMBA0'
    nlines=17
    
elif amtline=='B':
    edipath=r"h:\Peacock\USGSPostDoc\MonoBasin\MonoBasin_AMT\2011\MBB"
    metafn=r"h:\Peacock\USGSPostDoc\MonoBasin\MonoBasin_AMT\2011\MBB.txt"    
    edistem='ZMBB'
    nlines=21
    
    
reference_ellipsoid=5
zone='11N'
#get edi files
edilst=[os.path.join(edipath,edi) for edi in os.listdir(edipath) 
        if edi.find('.edi')>0]

#==============================================================================
# -------read in meta data in a useful way--------------------
#==============================================================================
mfid=file(metafn,'r')
mlines=mfid.readlines()

mlst=[]
mkeys=[key.lower() for key in mlines[0].strip().split()]
for jj,line in enumerate(mlines[1:nlines]):
    line=line.strip().split()
    if len(line)<2:
        break
    else:
        mlst.append({})
    for ii,key in enumerate(mkeys):
        if ii==0:        
            mlst[jj][key]=line[ii]
        elif ii==1:
            nedi=line[1][1:-1]
            nedi=nedi.split(',')
            mlst[jj][key]=[os.path.join(edipath,edistem+kk+'.edi') 
                            for kk in nedi]
        elif ii==2:
            mlst[jj][key]=Z.Z(os.path.join(edipath,line[ii]+'.edi'))
        else:
#            if ii==5:
#                #conversion of feet to meters
#                mlst[jj][key]=float(line[ii])
#            else:
#               mlst[jj][key]=float(line[ii])
            mlst[jj][key]=float(line[ii])
               
#==============================================================================
# read in impedance and stack for each station
#==============================================================================
ns=len(mlst)

for ll in range(ns):
    z1=mlst[ll]['model-sounding'].z.copy()
    kk=0
    zf=np.zeros_like(z1,dtype='complex')
    zf.resize((z1.shape[0],4))
    for ii in range(2):
        for jj in range(2):
            zxx=z1[:,ii,jj].flatten()
            zf[:,kk].real=sps.medfilt(zxx.real,kernel_size=7)
            zf[:,kk].imag=sps.medfilt(zxx.imag,kernel_size=7)
            kk+=1
    zf.resize((z1.shape[0],2,2))
    print zf.shape
    mlst[ll]['model-sounding'].z=zf
    mlst[ll]['model-sounding'].rewriteedi(znew=zf,
                                    zvarnew=np.zeros_like(zf).real)
    print mlst[ll]['model-sounding'].nedifn
    #------Input lats and longs-------------
    nfid=file(mlst[ll]['model-sounding'].nedifn,'r')
    nlines=nfid.readlines()
    nfid.close()

    #get lats and longs from utm **be sure to put in correct ellipsoid**    
    lat,lon=utm2ll.UTMtoLL(reference_ellipsoid,mlst[ll]['northing'],
                           mlst[ll]['easting'],zone)
                           
    #replace the lat and long lines in the edi file
    nlines[7]='LAT={0:.5f}\n'.format(lat)
    nlines[8]='LONG={0:.5f}\n'.format(lon)
    
    nlines[23]='REFLAT={0:.5f}\n'.format(lat)
    nlines[24]='REFLONG={0:.5f}\n'.format(lon)
    
    nfid=file(mlst[ll]['model-sounding'].nedifn,'w')
    nfid.writelines(nlines)
    nfid.close()
    
    
    



    
    
                                

