# -*- coding: utf-8 -*-
"""
Created on Wed Oct 05 11:54:41 2011

@author: a1185872
"""

import mtpy.core.edi as mtedi
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator,FormatStrFormatter
import matplotlib.gridspec as gridspec
import scipy.signal as sps

dirpath=r"g:\Peacock\PHD\Geothermal\Paralana"
stationlst=['pb44','pb49','pb13','pb09','pb04','pb25']#,'pbfm15ew']
#stationlst=['par15ew']
ns=len(stationlst)

plt.rcParams['font.size']=6
plt.rcParams['figure.subplot.left']=.09
plt.rcParams['figure.subplot.right']=.94
plt.rcParams['figure.subplot.bottom']=.145
plt.rcParams['figure.subplot.top']=.825
plt.rcParams['figure.subplot.wspace']=.01
plt.rcParams['figure.subplot.hspace']=.005

fig=plt.figure(1,[6,8],dpi=300)
plt.clf()

gs=gridspec.GridSpec(2,2,height_ratios=(2,1.5))
ax1r=fig.add_subplot(gs[0,0])
ax2r=fig.add_subplot(gs[0,1])
ax1p=fig.add_subplot(gs[1,0],sharex=ax1r)
ax2p=fig.add_subplot(gs[1,1],sharex=ax2r)

clst=[[(.3,0,0),(.8,.1,0)],[(0,0,.3),(0,.1,.8)],[(0,.3,0),(.1,.7,0)],
       [(.3,.3,0),(.8,.8,0)],[(0,.3,.3),(0,.8,.8)],[(.3,0,.3),(.8,0,.8)],
        [(0,0,0),(.5,.5,.5)]]

llst=[]
slst=[]
for ss,station in enumerate(stationlst):
#    station='pb09'
#    
#    #pb04 is pretty good
    
    if station.find('pb')==0:
#        basepath=os.path.join(dirpath,r"EDIFilesBaseSurvey\CFA")
#        injpath=os.path.join(dirpath,r"EDIFilesInjection\EDIfiles\CFA")
#        
#        basepath=os.path.join(dirpath,r"EDIFilesBaseSurvey\CFA\MedFilt")
#        injpath=os.path.join(dirpath,r"EDIFilesInjection\EDIfiles\CFA\MedFilt")
        basepath=os.path.join(r"c:\Users\jpeacock-pr\Documents\Paralana\Base\MedFilt_2")
        injpath=os.path.join(r"c:\Users\jpeacock-pr\Documents\Paralana\Post\MedFilt_2")
        
        ylimitsrte=(0,290)
        ylimitsrtm=(2.5,50)
        ylimitspte=(8,210)
        ylimitsptm=(25,220)
        xlimits=(.3,90)
        bfile=os.path.join(basepath,station+'f.edi')    
        if not os.path.exists(bfile):
            bfile=os.path.join(basepath,station+'sdr.edi')
            if not os.path.exists(bfile):
                bfile=os.path.join(basepath,station+'c.edi')
                if not os.path.exists(bfile):
                    bfile=os.path.join(basepath,station+'cf.edi')
    
        ifile=os.path.join(injpath,station+'f.edi')
        if not os.path.exists(ifile):
            ifile=os.path.join(injpath,station+'sdr.edi')
            if not os.path.exists(ifile):
                ifile=os.path.join(injpath,station+'c.edi')
                if not os.path.exists(ifile):
                    ifile=os.path.join(injpath,station+'cf.edi')
    elif station.find('par')==0:
        basepath=r"C:\Peacock\PHD\Geothermal\Paralana\ForwardModels\ParalanaModelBase"
        injpath=r"C:\Peacock\PHD\Geothermal\Paralana\ForwardModels\ParalanaModelBase\Water1"
        bfile=os.path.join(basepath,station+'.edi')
        ifile=os.path.join(injpath,station+'.edi')
        ylimitsr=(2.5,100)
        ylimitsp=(3,49)
        xlimits=(.08,90)
    
    c1=clst[ss][0]
    c2=clst[ss][1]
    m1='s'
    m2='o'
    
    ls1=':'
    ls2='--'
    ms=1
    lw=.5
    cs=1
    rs=30
    ps=25
    mb=1.0
    mi=1.0
    fdict={'size':8,'weight':'bold'}
    ldict={'size':6,'weight':'bold'}
    
    
    
    #get the impedance tensor
    impb=mtedi.Edi(bfile)
    impi=mtedi.Edi(ifile)
    ##get the determinant properties
    #dresb,dphaseb,detb=impb.getResPhaseDet()
    #dresi,dphasei,deti=impi.getResPhaseDet()
    #get the apparent resistivity and phase to check for static shift
    rpb=impb.Z.resistivity
    rpi=impi.Z.resistivity
    #compute static shift for each x and y component
    sx=np.sqrt(np.mean(rpb[0:15, 0, 1]/rpi[0:15, 0, 1]))
    sy=np.sqrt(np.mean(rpb[0:15, 1, 0]/rpi[0:15, 1, 0]))
    #sd=np.sqrt(np.mean(rpb.resdet[0:15]/rpi.resdet[0:15]))
    #make a static shift array
    staticshift=np.array([[sx],[sy]])
    #get period array
    if ss==6:
        period=impb.period/1.35
    else:
        period=impb.period
    #remove the local static shift
    #bresxy=rpb.resxy
    #iresxy=rpi.resxy*staticshift[0,0]**2
    #bresyx=rpb.resyx
    #iresyx=rpi.resyx*staticshift[1,0]**2
    bresxy=sps.medfilt(rpb[:, 0, 1], kernel_size=1)
    iresxy=sps.medfilt(rpi[:, 0, 1]*staticshift[0,0]**2, kernel_size=1)
    bresyx=sps.medfilt(rpb[:, 1, 0], kernel_size=1)
    iresyx=sps.medfilt(rpi[:, 1, 0]*staticshift[1,0]**2, kernel_size=1)
    
    #===============================================================================
    # Plot
    #===============================================================================
    
    #-------TE Resistivity-------------------
    bresxy_err = mb*impb.Z.resistivity_err[:, 0, 1]**2/impb.Z.resistivity_err[:, 0, 1].max()**2    
    iresxy_err = mi*impi.Z.resistivity_err[:, 0, 1]**2/impi.Z.resistivity_err[:, 0, 1].max()**2    
    bresyx_err = mb*impb.Z.resistivity_err[:, 1, 0]**2/impb.Z.resistivity_err[:, 1, 0].max()**2    
    iresyx_err = mi*impi.Z.resistivity_err[:, 1, 0]**2/impi.Z.resistivity_err[:, 1, 0].max()**2    
    
    erxyb=ax1r.errorbar(period,
                        mb*bresxy+ss*rs,
                        ls=ls1,
                        lw=lw,
                        color=c1,
                        yerr=bresxy_err,
                        marker=m1,
                        ms=ms,mec=c1,
                        ecolor=c1,
                        capsize=cs)
    erxyi=ax1r.errorbar(period,
                        mi*iresxy+.25*iresxy[0]+ss*rs,
                        ls=ls2,lw=lw,color=c2,
                        yerr=iresxy_err,
                        marker=m2, 
                        ms=ms, 
                        mec=c2,
                        ecolor=c2, 
                        capsize=cs)
    ax1r.fill_between(period,
                      mb*bresxy+ss*rs,
                      mi*iresxy+.25*iresxy[0]+ss*rs,
                      edgecolor='none',
                      facecolor=c2,
                      alpha=.5)
    llst.append(erxyb[0])
    llst.append(erxyi[0])
    if ss==6:
        slst.append('fm_b')
        slst.append('fm_i')
    else:
        slst.append(station+'_b')
        slst.append(station+'_i')
    #----Put a legend in the TE box----------
#    if ss==0:
#        ax1r.legend([erxyb[0],erxyi[0]],['Pre-injection','Post-injection'],
#                   prop=fdict,loc='lower right',ncol=1)
    
    
    #------TM Resistivity --------------------
    if ss==6:               
        eryxb=ax2r.errorbar(period,
                            mb*bresyx+1.05*ss*rs/5,
                            ls=ls1,
                            lw=lw,
                            color=c1,
                            yerr=bresyx_err,
                            marker=m1, 
                            ms=ms, 
                            mec=c1,
                            ecolor=c1, 
                            capsize=cs)
        eryxi=ax2r.errorbar(period,
                            mi*iresyx+.25*iresyx[0]+1.05*ss*rs/5,
                            ls=ls2,lw=lw,color=c2,
                            yerr=iresyx_err,
                            marker=m2, 
                            ms=ms, 
                            mec=c2,
                            ecolor=c2,
                            capsize=cs)
        ax2r.fill_between(period,
                          mb*bresyx+1.05*ss*rs/5,
                          mi*iresyx+.25*iresyx[0]+1.05*ss*rs/5,
                          edgecolor='none',
                          facecolor=c2,
                          alpha=.5)
    else:
        
        eryxb=ax2r.errorbar(period,mb*bresyx+ss*rs/5,ls=ls1,lw=lw,color=c1,
                          yerr=bresyx_err,marker=m1,ms=ms,mec=c1,
                          ecolor=c1,capsize=cs)
        eryxi=ax2r.errorbar(period,mi*iresyx+.25*iresyx[0]+ss*rs/5,ls=ls2,lw=lw,color=c2,
                          yerr=iresyx_err,marker=m2,ms=ms,mec=c2,
                          ecolor=c2,capsize=cs)
        ax2r.fill_between(period,mb*bresyx+ss*rs/5,mi*iresyx+.25*iresyx[0]+ss*rs/5,
                          edgecolor='none',facecolor=c2,alpha=.5)
#    if ss==0:
#        ax2r.legend([erxyb[0],erxyi[0]],['Pre-injection','Post-injection'],
#                   prop=fdict,loc='lower right',ncol=1)
    
    
    #------TE phase------------------
    bphase = impb.Z.phase
    iphase = impb.Z.phase
    bphase_err = impb.Z.phase_err
    iphase_err = impi.Z.phase_err
    
    ax1p.errorbar(period,mb*bphase[:, 0, 1]+ss*ps,ls=ls1,lw=lw,color=c1,
                 yerr=bphase_err[:, 0, 1]**2,ecolor=c1,marker=m1,ms=ms,mec=c1,
                 capsize=cs)
    if station=='pb44':
        ax1p.errorbar(period,mi*iphase[:, 0, 1]+.1*iphase[0, 0, 1]+ss*ps,ls=ls2,
                      lw=lw,color=c2,yerr=mi*iphase_err[:, 0, 1]**2,ecolor=c2,
                      marker=m2,ms=ms,mec=c2,capsize=cs)
        ax1p.fill_between(period,mb*bphase[:, 0, 1]+ss*ps,
                          mi*iphase[:, 0, 1]+.1*iphase[0, 0, 1]+ss*ps,
                          edgecolor='none',facecolor=c2,alpha=.5)
    else:            
        ax1p.errorbar(period,mi*iphase[:, 0, 1]+.25*iphase[0, 0, 1]+ss*ps,
                      ls=ls2,
                      lw=lw,color=c2,yerr=mi*iphase_err[:, 0, 1]**2,ecolor=c2,
                      marker=m2,ms=ms,mec=c2,capsize=cs)
        ax1p.fill_between(period,mb*bphase[:, 0, 1]+ss*ps,
                          mi*iphase[:, 0, 1]+.25*iphase[0, 0, 1]+ss*ps,
                          edgecolor='none',facecolor=c2,alpha=.5)
    
    #------TM phase--------------------------             
    ax2p.errorbar(period,mb*(bphase[:, 1, 0]-180)+ss*ps,ls=ls1,lw=lw,color=c1,
                 yerr=mb*bphase_err[:, 1, 0]**2,ecolor=c1,marker=m1,ms=ms,mec=c1,
                 capsize=cs)
    if station=='pb44':
        ax2p.errorbar(period,(mi*iphase[:, 1, 0]+.01*iphase[0, 1, 0])-180+ss*ps,
                      ls=ls2,
                      lw=lw,color=c2,yerr=mi*iphase_err[:, 1, 0],
                      ecolor=c2,marker=m2,
                      ms=ms,mec=c2,capsize=cs)
        ax2p.fill_between(period,mb*(bphase[:, 1, 0]+180)-ss*ps,
                          (mi*iphase[:, 1, 0]+.01*iphase[0, 1, 0])-180+ss*ps,
                          edgecolor='none',facecolor=c2,alpha=.5)
    else:
        ax2p.errorbar(period,(mi*iphase[:, 1, 0]+.01*iphase[0, 1, 0])-180+ss*ps,
                      ls=ls2,
                      lw=lw,color=c2,yerr=mi*iphase_err[:, 1, 0]**2,
                      ecolor=c2,marker=m2,
                      ms=ms,mec=c2,capsize=cs)
        ax2p.fill_between(period,mb*(bphase[:, 1, 0]+180)-ss*ps,
                          (mi*iphase[:, 1, 0]+.01*iphase[0, 1, 0])+180-ss*ps,
                          edgecolor='none',facecolor=c2,alpha=.5)
                 
for ii,ax in enumerate([ax1r,ax2r,ax1p,ax2p]):
    ax.set_xscale('log')
    ax.set_xlim(xlimits)
    if ii==0 or ii==1:
        ax.set_yscale('linear')
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2g'))
        plt.setp(ax.xaxis.get_ticklabels(),visible=False)
        if ii==0:
            ax.yaxis.set_label_coords(-.135,.5)
            ax.set_ylabel('App. Res. ($\mathbf{\Omega \cdot m}$)',
                          fontdict=fdict)
            ax.set_ylim(ylimitsrte)
            ax.yaxis.set_major_locator(MultipleLocator(rs))
            ax.yaxis.set_minor_locator(MultipleLocator(7.5))
            ax.set_yticklabels(['']+['{0:.0f}'.format(xx) 
                                for xx in np.arange(ylimitsrte[0]/1.25+20,
                                                    ylimitsrte[1]/1.25,20)])
            xx=ax.get_xlim()
            yy=ax.get_ylim()
            ax.text(xx[0]+.035,yy[1]-9,'Z$_{xy}$',fontdict=fdict,
                    horizontalalignment='left',
                    verticalalignment='top',
                    bbox={'facecolor':'white'})
        else:
            ax.yaxis.set_ticks_position('right')
#                plt.setp(ax.yaxis.get_ticklabels(),visible=False)
            ax.set_ylim(ylimitsrtm)
            ax.yaxis.set_major_locator(MultipleLocator(rs/5.))
            ax.yaxis.set_minor_locator(MultipleLocator(rs/15.))
            ax.set_yticklabels(['{0:.0f}'.format(xx) 
                                for xx in np.arange(7,
                                                    ylimitsrtm[1]/1.25,5)])
            
            xx=ax.get_xlim()
            yy=ax.get_ylim()
            ax.text(xx[0]+.035,yy[1]-1.65,'Z$_{yx}$',fontdict=fdict,
                    horizontalalignment='left',
                    verticalalignment='top',
                    bbox={'facecolor':'white'})
            
#            ax.text(.31,61,station,fontdict=fdict,horizontalalignment='left',
#                    verticalalignment='top',bbox={'facecolor':'white'})
    else:
        if ii==2:
            ax.set_ylabel('Phase (deg)',fontdict=fdict)
            ax.yaxis.set_label_coords(-.135,.5)
            ax.set_ylim(ylimitspte)
            ax.yaxis.set_major_locator(MultipleLocator(ps))
            ax.yaxis.set_minor_locator(MultipleLocator(ps/5))
            ax.set_yticklabels(['{0:.0f}'.format(xx) 
                                for xx in np.arange(ylimitspte[0],
                                                    ylimitspte[1]/1.25,5)])
        else:
#                plt.setp(ax.yaxis.get_ticklabels(),visible=False)
            ax.set_ylim(ylimitsptm)
            ax.yaxis.set_ticks_position('right')
            ax.yaxis.set_major_locator(MultipleLocator(ps))
            ax.yaxis.set_minor_locator(MultipleLocator(ps/5))
            ax.set_yticklabels(['{0:.0f}'.format(xx) 
                                for xx in np.arange(ylimitsptm[0],
                                                    ylimitsptm[1]/1.25,5)])
        ax.set_xlabel('Period (s)',fontdict=fdict)
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.3g'))
#    ax.grid(which='both',alpha=.3)
    
#ax.set_ylabel('App. Res. ($\mathbf{\Omega \cdot m}$)',
#         fontdict={'size':14,'weight':'bold'})
#ax2.set_ylabel('Phase(rad)', fontdict={'size':14,'weight':'bold'})
#ax2.set_xlabel('Period (s)',fontdict={'size':14,'weight':'bold'})
#ax2.set_xscale('log')
#ax.set_xlim(xmin=10**(np.floor(np.log10(period.min()))),
# xmax=10**(np.ceil(np.log10(period.max()))))
#ax2.set_ylim(ymin=0,ymax=90)
#ax2.yaxis.set_major_locator(MultipleLocator(10))
#ax2.yaxis.set_minor_locator(MultipleLocator(1))
#ax2.grid(True)
#
#ax2.legend([erxyb[0],erxyi[0],eryxb[0],eryxi[0]],['$E_x/B_y$ (base)','$E_x/B_y$ (inj)',
#           '$E_y/B_x$ (base)',
#           '$E_y/B_x$ (inj)'],loc=2,
#           markerscale=1,borderaxespad=.05,labelspacing=.08,
#           handletextpad=.15,borderpad=.05,ncol=2)
#plt.suptitle(station,fontsize=13,fontweight='bold')
fig.legend(llst,slst,ncol=len(llst)/2,prop={'size':6},loc='upper center',
           labelspacing=.08,
           columnspacing=.5,
           handletextpad=.1,
           markerscale=2)
plt.show()
