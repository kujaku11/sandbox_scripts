# -*- coding: utf-8 -*-
"""
Created on Wed May 25 16:39:30 2011

@author: a1185872
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sps
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LinearSegmentedColormap
import Z
from matplotlib.colorbar import *
from matplotlib.patches import Ellipse,Rectangle,Arrow
import pickle
import LatLongUTMconversion as utm2ll

#==============================================================================
# Inputs
#==============================================================================

ctype='data'    #data or fm for data or forward model
ttype='pt'      #or pt
plottype='pseudo'  #map of pseudo for map or pseudo section
sline='ew'      #line direction ns or ew only for pseudo section
diffyn='y'      #compute difference between surveys y or n
ptype='sqc'      #sq for square conductor, faults for faults
layeredyn='s'   #layered forward model y or n

#==============================================================================
# a few constants
#==============================================================================

refe=23
#phase tensor map
ptcmapdict={'red':((0.0,1.0,1.0),(1.0,1.0,1.0)),
            'green':((0.0,0.0,1.0),(1.0,0.0,1.0)),
            'blue':((0.0,0.0,0.0),(1.0,0.0,0.0))}
ptcmap=LinearSegmentedColormap('ptcmap',ptcmapdict,256)

#phase tensor map for difference (reverse)
ptcmapdictr={'red':((0.0,1.0,1.0),(1.0,1.0,1.0)),
            'green':((0.0,1.0,0.0),(1.0,1.0,0.0)),
            'blue':((0.0,0.0,0.0),(1.0,0.0,0.0))}
ptcmapr=LinearSegmentedColormap('ptcmapr',ptcmapdictr,256)

#resistivity tensor map for calculating delta
ptcmapdict2={'red':((0.0,0.0,1.0),(1.0,0.0,1.0)),
            'green':((0.0,0.0,0.0),(1.0,0.0,0.0)),
            'blue':((0.0,1.0,0.0),(1.0,1.0,0.0))}
ptcmap2=LinearSegmentedColormap('ptcmap2',ptcmapdict2,256)

#resistivity tensor map for calcluating resistivity difference
rtcmapdict3={'red':((0.0,0.0,0.0),(0.5,1.0,1.0),(1.0,1.0,0.0)),
            'green':((0.0,0.0,0.0),(0.5,1.0,1.0),(1.0,0.0,0.0)),
            'blue':((0.0,0.0,1.0),(0.5,1.0,1.0),(1.0,0.0,0.0))}
rtcmap3=LinearSegmentedColormap('rtcmap3',rtcmapdict3,256)

#resistivity tensor map for calcluating apparent resistivity
rtcmapdict3r={'red':((0.0,1.0,1.0),(0.5,1.0,1.0),(1.0,0.0,0.0)),
            'green':((0.0,0.0,0.0),(0.5,1.0,1.0),(1.0,0.0,0.0)),
            'blue':((0.0,0.0,0.0),(0.5,1.0,1.0),(1.0,1.0,1.0))}
rtcmap3r=LinearSegmentedColormap('rtcmap3r',rtcmapdict3r,256)

#borehole location
bhll=(139.72851,-30.2128)
bhz,bhe,bhn=utm2ll.LLtoUTM(refe,bhll[1],bhll[0])

ecmin=0
#===============================================================================
#Initialize parameters
#===============================================================================
if ctype=='data':    
    #set edipaths
    
    #set edipaths
    
    if ttype=='pt':
        edipathi=r"c:\Users\jpeacock-pr\Documents\Paralana\Post\MedFilt_2"
        edipathb=r"c:\Users\jpeacock-pr\Documents\Paralana\Base\MedFilt_2"

    elif ttype=='rt':
        edipathi=r"c:\Users\jpea562.EC\Documents\Paralana\InjectionEDIfiles\CFA"
        edipathb=r"c:\Users\jpea562.EC\Documents\Paralana\EDIFilesBaseSurvey\CFA"
        
    #make list of existing edifiles
    if diffyn=='y':
        edilst=[[os.path.join(edipathb,edib),os.path.join(edipathi,edii)] 
                for edib in os.listdir(edipathb) 
                for edii in os.listdir(edipathi)
                if edib.find('.edi')>0  if edib[0:4]==edii[0:4]]
        mfs=(3,5)
    elif diffyn=='n':
        edilst=[os.path.join(edipathi,edii) for edii in os.listdir(edipathi)
                if edii.find('.edi')>0]
        mfs=(1,1)                
    
    #pickle file name
    pkfn=r'c:\Users\jpeacock-pr\Documents\Paralana\PT_residual.pkl'    
    
    a=1
    #number of frequencies
    nf=43
    ns=len(edilst)
    noise=None
    #plot parameters
    #-------MAP-----------------------
    if plottype=='map':
        prange=[18,24,28,30,33,35]
        xlimits=(-3.4,3.4)
        ylimits=(-2.4,2.8)
#        xlimits=(-1.5,1.5)
#        ylimits=(-1.5,1.5)
        if ttype=='pt':
            esize=2
            if diffyn=='y':
                ecmax=.25
                fignum=10
            elif diffyn=='n':
                ecmax=90
                fignum=11
        elif ttype=='rt':
            esize=2
            if diffyn=='y':
                ecmax=2
                fignum=12
            elif diffyn=='n':
                ecmax=2
                fignum=13
                
    #------PSEUDO SECTION----------------------------    
    elif plottype=='pseudo':
        esize=1
        yspacing=.3
        ylimits=(-yspacing/2,nf*(yspacing)+yspacing/2)
        xstep=1
        xscaling=1
        if ttype=='rt':
            ecmax=2.50
        elif ttype=='pt':
            ecmax=.225
#            ecmax=90
        if sline=='ew':
            #pstationlst=['pb48']
            pstationlst=['pb{0:}'.format(ii) for ii in range(44,33,-1)]+\
                        ['pb{0:}'.format(ii) for ii in range(23,34)]
            #stationlst.remove('pb27')
            fignum=14
        elif sline=='ns':
            pstationlst=['pb{0:}'.format(ii) for ii in range(22,11,-1)]+\
                        ['pb0{0:}'.format(ii) for ii in range(1,10)]+\
                        ['pb10','pb11']
            pstationlst.remove('pb05')
            pstationlst.remove('pb06')
            pstationlst.remove('pb12')
            fignum=15



#---------Forward Model-------------------------------------------------------
elif ctype=='fm':
    #set edipaths
    if layeredyn=='n':
        edipathb=r"c:\Peacock\PHD\Geothermal\Paralana\ForwardModels\TensorTest\HalfSpace"
        if ptype=='sq':
            edipathi=r"c:\Peacock\PHD\Geothermal\Paralana\ForwardModels\TensorTest\NearSquareConductor"
            if ttype=='rt':            
                fignum=2
            elif ttype=='pt':
                fignum=6
        elif ptype=='sqc':
            edipathi=r"c:\Peacock\PHD\Geothermal\Paralana\ForwardModels\TensorTest\HalfSpaceSQC"
            if ttype=='rt':            
                fignum=22
                if diffyn=='y':
                    ecmax=99
                elif diffyn=='n':
                    ecmax=2.346
                    ecmin=2.03
            elif ttype=='pt':
                fignum=26
                ecmax=2.0
        elif ptype=='sqr':            
            edipathi=r"c:\Peacock\PHD\Geothermal\Paralana\ForwardModels\TensorTest\HalfSpaceSQR"
            if ttype=='rt':            
                fignum=32
                if diffyn=='y':
                    ecmax=50
                elif diffyn=='n':
                    ecmax=2.38
                    ecmin=2.26
            elif ttype=='pt':
                fignum=36
                ecmax=.2
        elif ptype=='faults':
            edipathi=r"c:\Peacock\PHD\Geothermal\Paralana\ForwardModels\TensorTest\Faults"
            if ttype=='rt':            
                fignum=3
            elif ttype=='pt':
                fignum=7
    elif layeredyn=='y':
        edipathb=r"c:\Peacock\PHD\Geothermal\Paralana\ForwardModels\TensorTest\LayeredHalfSpace"
        if ptype=='sq':
            edipathi=r"c:\Peacock\PHD\Geothermal\Paralana\ForwardModels\TensorTest\NEConductor"
            if ttype=='rt':            
                fignum=4
            elif ttype=='pt':
                fignum=8
        elif ptype=='faults':
            edipathi=r"c:\Peacock\PHD\Geothermal\Paralana\ForwardModels\TensorTest\NEFaults"
            if ttype=='rt':            
                fignum=5
            elif ttype=='pt':
                fignum=9
    else:
        edipathb=r"c:\Peacock\PHD\Geothermal\Paralana\ForwardModels\ParalanaBase\BaseFineMesh"
        edipathi=r"c:\Peacock\PHD\Geothermal\Paralana\ForwardModels\ParalanaBase\BaseFineMeshNEfaults"
        if ttype=='rt':
            fignum=10
#            ecmax=1.2
            ecmax=.42
        elif ttype=='pt':
            fignum=1
#            ecmax=.0016
            ecmax=90
            ecmin=88

    pkfn='C:\\Peacock\\Python\\'+ttype.upper()+'FM'+ptype+diffyn+layeredyn+'.pkl'
#    pkfn=r'c:\Users\Own er\Documents\PHD\Geothermal\Paralana\RTBAComparisonFM.pkl'
    
    #make list of existing edifiles
    if diffyn=='y':
        edilst=[[os.path.join(edipathb,edib),os.path.join(edipathi,edii)] 
                for edib in os.listdir(edipathb) 
                for edii in os.listdir(edipathi)
                if edib.find('.')>0  if edib[0:-4]==edii[0:-4]]
    else:
        edilst=[os.path.join(edipathi,edii) for edii in os.listdir(edipathi) 
                if edii.find('.edi')]
    

#    #set parameters for plotting
#    if diffyn=='y':
#        if ptype=='sq':
#            if layeredyn=='y':
#                if ttype=='rt':
#                    ecmax=1.5
#                elif ttype=='pt':
#                    ecmax=.012
#            elif layeredyn=='n':
#                if ttype=='rt':
#                    ecmax=11
#                elif ttype=='pt':
#                    ecmax=.20
#        elif ptype=='faults':
#            if layeredyn=='y':
#                if ttype=='rt':
#                    ecmax=11
#                elif ttype=='pt':
#                    ecmax=.01
#            elif layeredyn=='n':
#                if ttype=='rt':
#                    ecmax=7
#                elif ttype=='pt':
#                    ecmax=.012
#        else:
#            if ttype=='rt':
#                ecmax=.002
#            elif ttype=='pt':
#                ecmax=2.0
#    else:
#        if ttype=='rt':
#            ecmax=2.269
#        elif ttype=='pt':
#            ecmax=1.0
            
    #number of frequencies
    if layeredyn=='y' or layeredyn=='n':
        nf=14
    else:
        nf=12
    ns=len(edilst)


    a=1
    noise=None
    yspacing=1
    xscaling=1
    xstep=2
    ncols=3
    mfs=(1,1)
    if plottype=='map':
#        prange=[4,5,6,7,8,9]
        prange=[1,2,3,4,5,6]
        xlimits=(-3.4,3.8)
        ylimits=(-3.4,3.4)
        esize=.7
    elif plottype=='pseudo':
        prange=range(nf)
        xlimits=(-7,7)
        ylimits=(-1,(nf+1)*yspacing)
        if diffyn=='y':
            esize=5
        elif diffyn=='n':
            esize=.1

    if sline=='ew':
        pstationlst=['par0{0}ew'.format(ii) for ii in range(1,10)]+\
                    ['par{0}ew'.format(ii) for ii in range(10,32)]
    if sline=='ns':
        pstationlst=['par12{0}'.format(ii) for ii in range(19,9,-1)]+\
                    ['par'+str(ii) for ii in [30,32,43,'15ew',56,57,68,69,710]]+\
                    ['par120{0}'.format(ii) for ii in range(1,10)]
    

if not os.path.isfile(pkfn):
    azimutharr=np.zeros((nf,ns))
    phimaxarr=np.zeros((nf,ns))
    phiminarr=np.zeros((nf,ns))
    betaarr=np.zeros((nf,ns))
    colorarr=np.zeros((nf,ns))
    
    latlst=np.zeros(ns)
    lonlst=np.zeros(ns)

    stationlst=[]
    
    for ss,station in enumerate(edilst):
        
        if ttype=='rt':        
            if diffyn=='y':
                #make a data type Z      
                z1=Z.Z(station[0])
                z2=Z.Z(station[1])
                
                stationlst.append(z1.station)        
                
                sz,se,sn=utm2ll.LLtoUTM(refe,z1.lat,z1.lon)
                latlst[ss]=(sn-bhn)/1000.
                lonlst[ss]=(se-bhe)/1000.
                
                #get the phase tensor information 
                pt1=z1.getResTensor(rotate=180)
                pt2=z2.getResTensor(rotate=180)
            
                
                #loop over period plotting the difference between phase tensors
                period=z1.period
                nf=len(period)
                
                for ii in range(nf):
                    
                    if noise!=None:
                        sigman=np.sqrt(abs(pt1.rho[ii,0,1]*pt1.rho[ii,1,0]))*noise
                        pt1.rho[ii]=pt1.rho[ii]+sigman*np.random.normal(size=(2,2))
                        pt2.rho[ii]=pt2.rho[ii]+sigman*np.random.normal(size=(2,2))
                    #calculate the difference between the two phase tensor ellipses
                    
#                    rho=np.eye(2)-\
#                            (np.dot(np.linalg.inv(pt2.rho[ii]),pt1.rho[ii])+
#                            np.dot(pt1.rho[ii],np.linalg.inv(pt2.rho[ii])))/2
                    rho=np.eye(2)-(np.dot(np.linalg.inv(pt1.rho[ii]),
                                   pt2.rho[ii]))
                            
                    pi1=.5*np.sqrt((rho[0,0]-rho[1,1])**2+(rho[0,1]+rho[1,0])**2)
                    pi2=.5*np.sqrt((rho[0,0]+rho[1,1])**2+(rho[0,1]-rho[1,0])**2)
                    
                    phimax=pi1+pi2
                    phimin=pi2-pi1
                    
                    alpha=.5*np.arctan((rho[0,1]+rho[1,0])/(rho[0,0]-rho[1,1]))
                    beta=.5*np.arctan((rho[0,1]-rho[1,0])/(rho[0,0]+rho[1,1]))
                    
                    azimuth=(alpha-beta)*180/np.pi
                    
                    ecolor=np.sign(pt1.rhomax[ii]-pt2.rhomin[ii])*\
                            (abs(rho.min())+abs(rho.max()))/2
                    
                    #put things into arrays
                    phimaxarr[ii,ss]=phimax
                    phiminarr[ii,ss]=phimin
                    azimutharr[ii,ss]=azimuth
                    betaarr[ii,ss]=pt1.rhodet[ii]-pt2.rhodet[ii]
                    colorarr[ii,ss]=ecolor
                    
            elif diffyn=='n':
                
                z1=Z.Z(station)

                pt1=z1.getResTensor(rotate=0)
                    
                stationlst.append(z1.station)
                period=z1.period
                
                sz,se,sn=utm2ll.LLtoUTM(refe,z1.lat,z1.lon)
                latlst[ss]=(sn-bhn)/1000.
                lonlst[ss]=(se-bhe)/1000.
                
                phimaxarr[:,ss]=pt1.rhomax
                phiminarr[:,ss]=pt1.rhomin
                azimutharr[:,ss]=pt1.rhoazimuth
                colorarr[:,ss]=np.log10(pt1.rhodet)
        elif ttype=='pt':
            
            if diffyn=='y':
                #make a data type Z      
                z1=Z.Z(station[0])
                z2=Z.Z(station[1])
                
                stationlst.append(z1.station)        
                
                sz,se,sn=utm2ll.LLtoUTM(refe,z1.lat,z1.lon)
                latlst[ss]=(sn-bhn)/1000.
                lonlst[ss]=(se-bhe)/1000.
                
                #get the phase tensor information 
                pt1=z1.getPhaseTensor(rotate=180)
                pt2=z2.getPhaseTensor(rotate=180)
                if noise!=None:
                    sigman=np.sqrt(abs(pt1.phi[ii,0,1]*pt1.phi[ii,1,0]))*noise
                    pt1.phi[ii]=pt1.phi[ii]+sigman*np.random.normal(size=(2,2))
                    pt2.phi[ii]=pt2.phi[ii]+sigman*np.random.normal(size=(2,2))
                #calculate the difference between the two phase tensor ellipses
                for ii in range(nf):
#                    phi=np.eye(2)-\
#                        (np.dot(np.linalg.inv(pt2.phi[ii]),pt1.phi[ii])+
#                        np.dot(pt1.phi[ii],np.linalg.inv(pt2.phi[ii])))/2 
                    phi=np.eye(2)-(np.dot(np.linalg.inv(pt1.phi[ii]),
                                    pt2.phi[ii]))            
                
                    #compute the trace        
                    tr=phi[0,0]+phi[1,1]
                    #Calculate skew of phi and the cooresponding error
                    skew=phi[0,1]-phi[1,0]
                    #calculate the determinate and determinate error of phi
                    phidet=abs(np.linalg.det(phi))
                    
                    #calculate reverse trace and error
                    revtr=phi[0,0]-phi[1,1]
                    
                    #calculate reverse skew and error
                    revskew=phi[1,0]+phi[0,1]
                    
                    beta=.5*np.arctan2(skew,tr)*(180/np.pi)
                    alpha=.5*np.arctan2(revskew,revtr)*(180/np.pi)
                    
                    #need to figure out why azimuth is off by 90 deg
                    azimuth=(alpha-beta)                   
                   
                    #calculate phimax
                    phimax=np.sqrt(abs((.5*tr)**2+(.5*skew)**2))+\
                            np.sqrt(abs((.5*tr)**2+(.5*skew)**2-np.sqrt(phidet)**2))
                        
                    #calculate minimum value for phi
                    if phidet>=0:
                        phimin=np.sqrt(abs((.5*tr)**2+(.5*skew)**2))-\
                        np.sqrt(abs((.5*tr)**2+(.5*skew)**2-np.sqrt(phidet)**2))
                    elif phidet<0:
                        phimin=-1*np.sqrt(abs((.5*tr)**2+(.5*skew)**2))-np.sqrt(abs(
                                    (.5*tr)**2+(.5*skew)**2-(np.sqrt(phidet))**2))
        #            ecolor=(abs(phi.min())+abs(phi.max()))/2
#                    ecolor=(abs(phi.min())+abs(phi.max()))/2
                    ecolor=np.sqrt(abs(phi.min())*abs(phi.max()))
                    
                    #put things into arrays
                    phimaxarr[ii,ss]=phimax
                    phiminarr[ii,ss]=phimin
                    azimutharr[ii,ss]=azimuth
                    betaarr[ii,ss]=abs(beta)
                    colorarr[ii,ss]=ecolor
            elif diffyn=='n':
                    
                z1=Z.Z(station)

                pt1=z1.getPhaseTensor()
                    
                stationlst.append(z1.station)
                period=z1.period
                
                sz,se,sn=utm2ll.LLtoUTM(refe,z1.lat,z1.lon)
                latlst[ss]=(sn-bhn)/1000.
                lonlst[ss]=(se-bhe)/1000.
                
                phimaxarr[:,ss]=pt1.phimax
                phiminarr[:,ss]=pt1.phimin
                azimutharr[:,ss]=pt1.azimuth
                colorarr[:,ss]=pt1.phimin*180/np.pi
                betaarr[:,ss]=pt1.beta
            
            
    #===============================================================================
    # Filter the arrays if desired
    #===============================================================================
    phimaxarr=sps.medfilt2d(phimaxarr,kernel_size=mfs)
    phiminarr=sps.medfilt2d(phiminarr,kernel_size=mfs)
    azimutharr=sps.medfilt2d(azimutharr,kernel_size=mfs)
    betaarr=sps.medfilt2d(betaarr,kernel_size=mfs)
    colorarr=sps.medfilt2d(colorarr,kernel_size=mfs)
    
    #normalize ecolor
    #cmax=colorarr.max()

#    ecolorarr=colorarr/cmax
#    cpass=np.where(abs(ecolorarr)>1)
#    ecolorarr[cpass]=1

    #===============================================================================
    # Pickle results so don't have to reload them everytime
    #===============================================================================
    fid=file(pkfn,'w')
    pickle.dump((phimaxarr,phiminarr,azimutharr,betaarr,colorarr,latlst,lonlst,
                 stationlst,z1.period),fid)
    fid.close()

#==============================================================================
# Print what you are plotting
#==============================================================================
print 'pkfn:\t',pkfn
print 'ctype:\t',ctype
print 'tensor:\t',ttype
print 'Plotting:\t',plottype
if plottype=='pseudo':
    print 'Line Dir:\t',sline
print 'Diff:\t',diffyn
if ctype=='fm':
    print 'Model:\t',ptype
    print 'Layered:\t',layeredyn

#===============================================================================
# Plot ellipses in map view
#===============================================================================

#load pickled file
pkfid=file(pkfn,'r')
phimaxarr,phiminarr,azimutharr,betarr,ecolorarr,latlst,lonlst,stationlst,period=\
                                                            pickle.load(pkfid)
pkfid.close()

print 'ecolorarr.max()= {0:.5f}'.format(ecolorarr.max())

if plottype=='map':

    ecolorarr=np.nan_to_num(ecolorarr)
    nrows=len(prange)/ncols
    
    plt.rcParams['font.size']=6
    plt.rcParams['figure.subplot.left']=.1
    plt.rcParams['figure.subplot.right']=.92
    plt.rcParams['figure.subplot.bottom']=.08
    plt.rcParams['figure.subplot.top']=.95
    plt.rcParams['figure.subplot.hspace']=.005
    plt.rcParams['figure.subplot.wspace']=.005
    
    
    emax=2*esize
    fig=plt.figure(fignum,[14,14],dpi=300)
    plt.clf()
    for ii,ff in enumerate(prange,1):
        ax1=fig.add_subplot(nrows,ncols,ii,aspect='equal')
        for ss in range(ns):
            if ctype=='data':
                eheightd=phiminarr[ff,ss]/(np.median(phimaxarr[ff,:])*3)*esize
                ewidthd=phimaxarr[ff,ss]/(np.median(phimaxarr[ff,:])*3)*esize
            else:
                eheightd=phiminarr[ff,ss]/phimaxarr[ff,:].max()*esize
                ewidthd=phimaxarr[ff,ss]/phimaxarr[ff,:].max()*esize
            
            if eheightd>emax or ewidthd>emax:
                pass
                
            else:
                if diffyn=='y':
                    ellipd=Ellipse((lonlst[ss],latlst[ss]),
                                   width=ewidthd,
                                   height=eheightd,
                                   angle=azimutharr[ff,ss]-90)
                elif diffyn=='n':
                    ellipd=Ellipse((lonlst[ss],latlst[ss]),
                                   width=ewidthd,
                                   height=eheightd,
                                   angle=azimutharr[ff,ss])
            #color ellipse
            if ttype=='pt':
                if diffyn=='y':
                    cvar=ecolorarr[ff,ss]/ecmax
                elif diffyn=='n':
                    cvar=ecolorarr[ff,ss]/90
                if abs(cvar)>1:
                    ellipd.set_facecolor((1,0,.1))
                else:
                    ellipd.set_facecolor((1,1-abs(cvar),.1))
            elif ttype=='rt':
                if diffyn=='y':
                    cvar=betarr[ff,ss]/ecmax
                    if cvar<0:
                        if cvar<-1:
                            ellipd.set_facecolor((0,0,1))
                        else:
                            ellipd.set_facecolor((1-abs(cvar),1-abs(cvar),1))
                    else:
                        if cvar>1:
                            ellipd.set_facecolor((1,0,0))
                        else:
                            ellipd.set_facecolor((1,1-abs(cvar),1-abs(cvar)))
                elif diffyn=='n':
                    cvar=(ecolorarr[ff,ss]-ecmin)/(ecmax-ecmin)
                    if cvar>.5:
                        if cvar>1:
                            ellipd.set_facecolor((0,0,1))
                        else:
                            ellipd.set_facecolor((1-abs(cvar),1-abs(cvar),1))
                    else:
                        if cvar<-1:
                            ellipd.set_facecolor((1,0,0))
                        else:
                            ellipd.set_facecolor((1,1-abs(cvar),1-abs(cvar)))
            ax1.add_patch(ellipd)
                
        
        ax1.set_xlim(xlimits)
        ax1.set_ylim(ylimits)
    
        ax1.text(xlimits[0]+.20,ylimits[1]-.2,'T={0:.2g} s'.format(period[ff]),
                 verticalalignment='top',horizontalalignment='left',
                 fontdict={'size':8,'weight':'bold'},
                 bbox={'facecolor':'white'})
        ax1.text(0,0,'X',
                 verticalalignment='center',
                 horizontalalignment='center',
                 fontdict={'size':9,'weight':'bold'})
        ellips=Ellipse((xlimits[0]+.85,ylimits[0]+.65),width=1,height=1,
                       angle=0)
        ellips.set_facecolor((.1,.1,.1))
        ax1.add_artist(ellips)
        ax1.grid(alpha=.2)
        
        if ctype=='fm':
            ax1.text(xlimits[0]+.20,ylimits[0]+1.4,
                     '$\Delta$={0:.2g}'.format(phimaxarr[ff,:].max()*a),
                     horizontalalignment='left',
                     verticalalignment='bottom',
                     bbox={'facecolor':'white'})
        elif ctype=='data':
            ax1.text(xlimits[0]+.20,ylimits[0]+1.4,
                     '$\Delta$={0:.2g}'.format(np.median(phimaxarr[ff,:])*3),
                     horizontalalignment='left',
                     verticalalignment='bottom',
                     bbox={'facecolor':'white'})
    
        if ii>nrows:
            ax1.set_xlabel('easting (km)',fontdict={'size':9,'weight':'bold'})
        if ii<(nrows-1)*ncols+1:
            ax1.xaxis.set_ticklabels(['' for hh in 
                                        range(len(ax1.xaxis.get_ticklabels()))])
        
        if ii==1 or ii==ncols+1 or ii==2*ncols+1 or ii==3*ncols+1:
            pass
        else:
            ax1.yaxis.set_ticklabels(['' for hh in 
                                        range(len(ax1.yaxis.get_ticklabels()))])
        if ii==ncols*int(nrows/2)+1 or ii==1:
            ax1.set_ylabel('northing (km)',fontdict={'size':9,'weight':'bold'})
    
    #add colorbar
    ax2=fig.add_subplot(1,1,1)
    ax2.set_visible(False)
    cbax=make_axes(ax2,shrink=.99,fraction=.015,pad=10.2)
    if ttype=='rt':
        if diffyn=='y':
            cbx=ColorbarBase(cbax[0],cmap=rtcmap3,
                             norm=Normalize(vmin=-ecmax,vmax=ecmax),
                             orientation='vertical',format='%.2g')
            cbx.set_label('App. Res. ($\Omega \cdot$m) ',
                          fontdict={'size':7,'weight':'bold'})
        if diffyn=='n':
            cbx=ColorbarBase(cbax[0],cmap=rtcmap3r,
                             norm=Normalize(vmin=ecmin,vmax=ecmax),
                             orientation='vertical',format='%.2g')
            cbx.set_label('App. Res. ($\Omega \cdot$m) ',
                          fontdict={'size':7,'weight':'bold'})
                         
    elif ttype=='pt':
        if diffyn=='y':
            cbx=ColorbarBase(cbax[0],cmap=ptcmap,norm=Normalize(vmin=0,vmax=ecmax),
                             orientation='vertical')
            cbx.set_label('(|$\Delta_{max}$|+|$\Delta_{min}$|)/2 ',
                          fontdict={'size':7,'weight':'bold'})
        elif diffyn=='n':
            cbx=ColorbarBase(cbax[0],cmap=ptcmap,norm=Normalize(vmin=0,vmax=90),
                             orientation='vertical')
            cbx.set_label('Phimin (deg) ',
                          fontdict={'size':7,'weight':'bold'})
                         
    #cbx.set_label('Beta',fontdict={'size':7,'weight':'bold'})
    
    plt.show()


#==============================================================================
# Plot Data Pseudo section
#==============================================================================

elif plottype=='pseudo':
    if ctype=='data':
        sdict=dict([(station[0:4],ii) for ii,station in enumerate(stationlst)])
    
        pslst=[]
        xlabels=[]
        offsetlst=[]
        for pss in pstationlst:
            try:
                pslst.append(sdict[pss])
                xlabels.append(pss[2:4])
                if sline=='ew':
                    offsetlst.append(lonlst[sdict[pss]])
                elif sline=='ns':
                    offsetlst.append(latlst[sdict[pss]])
            except KeyError:
                pass
            
    if ctype=='fm':
        sdict=dict([(station,ii) for ii,station in enumerate(stationlst)])
    
        pslst=[]
        xlabels=[]
        offsetlst=[]
        for pss in pstationlst:
            try:
                pslst.append(sdict[pss])
                xlabels.append(pss[3:5])
                if sline=='ew':
                    offsetlst.append(lonlst[sdict[pss]])
                elif sline=='ns':
                    offsetlst.append(latlst[sdict[pss]])
            except KeyError:
                pass
    
    nx=len(xlabels)
    xtks=list(offsetlst)
    xtks.sort()
    xtks=np.array(xtks)
    plt.rcParams['font.size']=8
    plt.rcParams['figure.subplot.left']=.1
    plt.rcParams['figure.subplot.right']=.94
    plt.rcParams['figure.subplot.bottom']=.08
    plt.rcParams['figure.subplot.top']=.95
    plt.rcParams['figure.subplot.hspace']=.05
    
    emax=5*esize
    #create a plot instance
    fig=plt.figure(fignum,[8,6],dpi=300)
    plt.clf()
    ax1=fig.add_subplot(1,1,1,aspect='equal')
    
    for jj,ss in enumerate(pslst):
        for ff in range(nf):
            if ctype=='data':
                eheightd=phiminarr[ff,ss]/(np.median(phimaxarr[:,:])*3)*esize
                ewidthd=phimaxarr[ff,ss]/(np.median(phimaxarr[:,:])*3)*esize
#                eheightd=phiminarr[ff,ss]/phimaxarr[:,:].max()*esize
#                ewidthd=phimaxarr[ff,ss]/phimaxarr[:,:].max()*esize
            else:
                eheightd=phiminarr[ff,ss]/phimaxarr[:,:].max()*esize
                ewidthd=phimaxarr[ff,ss]/phimaxarr[:,:].max()*esize
            
            if eheightd>emax or ewidthd>emax:
                pass
            else:
                if diffyn=='y':
                    if sline=='ew':
                        ellipd=Ellipse((lonlst[ss]*xscaling,yspacing*(nf-ff)),
                                       width=ewidthd,
                                       height=eheightd,
                                       angle=90-azimutharr[ff,ss])
                    elif sline=='ns':
                        ellipd=Ellipse((latlst[ss]*xscaling,yspacing*(nf-ff)),
                                       width=ewidthd,
                                       height=eheightd,
                                       angle=azimutharr[ff,ss])
                elif diffyn=='n':
                    if sline=='ew':
                        ellipd=Ellipse((lonlst[ss]*xscaling,yspacing*(nf-ff)),
                                       width=ewidthd,
                                       height=eheightd,
                                       angle=azimutharr[ff,ss])
                    elif sline=='ns':
                        ellipd=Ellipse((latlst[ss]*xscaling,yspacing*(nf-ff)),
                                       width=ewidthd,
                                       height=eheightd,
                                       angle=azimutharr[ff,ss])
            
           

            #color ellipse
            if ttype=='pt':
                if diffyn=='y':
                    cvar=ecolorarr[ff,ss]/ecmax
                elif diffyn=='n':
                    cvar=ecolorarr[ff,ss]/ecmax
                if abs(cvar)>1:
                    ellipd.set_facecolor((1,0,.1))
                else:
                    ellipd.set_facecolor((1,1-abs(cvar),.1))
            elif ttype=='rt':
                cvar=betarr[ff,ss]/ecmax
                if cvar<0:
                    if cvar<-1:
                        ellipd.set_facecolor((0,0,1))
                    else:
                        ellipd.set_facecolor((1-abs(cvar),1-abs(cvar),1))
                else:
                    if cvar>1:
                        ellipd.set_facecolor((1,0,0))
                    else:
                        ellipd.set_facecolor((1,1-abs(cvar),1-abs(cvar)))
            
            ax1.add_artist(ellipd)              
    
    yticklabels=[]
    for yy in np.arange(start=1,stop=nf+1,step=2):
        if period[nf-yy]<100:
            yticklabels.append('{0:.3g}'.format(period[nf-yy]))
        else:
            yticklabels.append('{0:.0f}'.format(period[nf-yy]))
#    yticklabels=['%2.3g' % period[nf-ii] for ii in np.arange(start=1,stop=nf+1,
#                 step=2)]
    ax1.set_ylabel('period (s)',fontdict={'size':9,'weight':'bold'})
    ax1.set_yticks(np.arange(start=yspacing,stop=yspacing*nf+1,step=2*yspacing))
    ax1.set_yticklabels(yticklabels)
    
    #ax1.xaxis.set_tick_params(labelbottom='on',labeltop='on')
    
    ax1.set_xticks(xtks[range(0,nx,xstep)])
    #ax1.xaxis.set_ticklabels(['{0:.2g}'.format(nn) for nn in xtks[range(0,nx+1,2)]])
    ax1.set_xticklabels([xlabels[xx] for xx in range(0,nx,xstep)])
    ax1.set_xlim(min(offsetlst)-.5,max(offsetlst)+.5)
    ax1.set_ylim(ylimits)
    ax1.set_xlabel('station',fontdict={'size':10,'weight':'bold'})
    #ax1.set_title('Before and After Injection',fontdict={'size':12,'weight':'bold'})
    ax1.grid()
    
    
    ax4=make_axes(ax1,shrink=.5,fraction=.1,orientation='vertical',pad=.005)
    if ttype=='pt':
        if diffyn=='y':
            cb1=ColorbarBase(ax4[0],cmap=ptcmap,norm=Normalize(vmin=0,vmax=ecmax),
                             orientation='vertical')
        elif diffyn=='n':
            cb1=ColorbarBase(ax4[0],cmap=ptcmap,norm=Normalize(vmin=0,vmax=ecmax),
                             orientation='vertical')
#        cb1.set_label('(|$\Delta_{max}$|+|$\Delta_{min}$|)/2')
        cb1.set_label('$\sqrt{\Delta \Phi_{max} \, \Delta \Phi_{min}}$')
    elif ttype=='rt':
        cb1=ColorbarBase(ax4[0],cmap=rtcmap3,norm=Normalize(vmin=-ecmax,vmax=ecmax),
                         orientation='vertical')
        cb1.set_label('App. Res. ($\Omega \cdot$m) ',
                      fontdict={'size':7,'weight':'bold'})
    
    
    #plt.savefig(os.path.join(savepath,station+'PhaseTensorsComparison.png'))
    #plt.close()
    plt.show()
