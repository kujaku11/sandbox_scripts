# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 15:17:26 2013

@author: jpeacock
"""

import simplekml as skml
import numpy as np
import mtpy.utils.latlongutmconversion as ll2utm
import matplotlib.pyplot as plt
north0=4212750.0
east0=308650.0

dx=2000.0
dy=6000.0

nx=15
ny=8

thetar=-10*np.pi/180.

east=[]
north=[]
kmlfid=skml.Kml()
fig=plt.figure(1,figsize=[8,8],dpi=300)
ax=fig.add_subplot(1,1,1,aspect='equal')
for yy in range(ny):
    for xx in range(nx):
        eastx=east0+dx*xx
        northy=north0-dy*yy
        east.append(eastx)
        north.append(northy)
        ax.scatter(eastx,northy,marker='v')
        eastr=east0+dx*xx*np.cos(thetar)-dy*yy*np.sin(thetar)
        northr=north0-dy*yy*np.cos(thetar)-xx*dx*np.sin(thetar)
        ax.scatter(eastr,northr,marker='v',color='r')
        xlat,ylon=ll2utm.UTMtoLL(23,northr,eastr,'11S')
        kmlfid.newpoint(name=''.format(yy,xx),coords=[(ylon,xlat)])
        
kmlfid.save(r"c:\Documents and Settings\jpeacock\My Documents\MonoBasin\ProposedMTSitesNoNames.kml")

#east=np.array(east)*np.cos(thetar)
#north=np.array(north)*np.cos(-thetar)
#
#plt.scatter(east,north)
#x,y=np.meshgrid(east,north)
#rmatrix=np.array([[np.cos(thetar),-np.sin(thetar)],
#                   [np.sin(thetar),np.cos(thetar)]])
#z=np.array([east,north])



