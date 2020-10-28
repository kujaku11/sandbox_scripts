# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(Jared Peacock)s
"""

import numpy as np
import mtpy.core.edi as mtedi
import mtpy.analysis.pt as mtpt
import os
import matplotlib.pyplot as plt

# edipath1=r"c:\Users\Own er\Documents\PHD\Geothermal\Paralana\EDIFilesBaseSurvey\March2010"
# edipath2=r"c:\Users\Own er\Documents\PHD\Geothermal\Paralana\EDIFilesBaseSurvey\May2010"
# edipath3=r"c:\Users\Own er\Documents\PHD\Geothermal\Paralana\EDIFilesBaseSurvey\March2011"

edipath1 = r"g:\Peacock\PHD\Geothermal\Paralana\EDIFilesBaseSurvey\March2010\DR"
edipath2 = r"g:\Peacock\PHD\Geothermal\Paralana\EDIFilesBaseSurvey\May2010\DR"
edipath3 = r"g:\Peacock\PHD\Geothermal\Paralana\EDIFilesBaseSurvey\March2011\DR"

sv_path = r"c:\Users\jpeacock-pr\Documents\Paralana"

ediext = "cdr.edi"
# station='pb23'
#
stationlst = ["pb0" + str(ii) for ii in range(1, 10)] + [
    "pb" + str(ii) for ii in range(10, 55)
]

stationclst = list(stationlst)
replst = []
preplst = []
ptlst = []

for ss, station in enumerate(stationlst):
    implst = []
    colorlst = []
    lines = ["{0:^72}\n".format("-" * 30 + station + "-" * 30)]
    lines.append(
        "{0:^12}{1:^12}{2:^12}\n".format("frequency(Hz)", "z_det(%)", "pt_det(%)")
    )
    if os.path.isfile(os.path.join(edipath1, station + ediext)) == True:
        imp1 = os.path.join(edipath1, station + ediext)
        implst.append(imp1)

    if os.path.isfile(os.path.join(edipath2, station + ediext)) == True:
        imp2 = os.path.join(edipath2, station + ediext)
        implst.append(imp2)
    if os.path.isfile(os.path.join(edipath3, station + ediext)) == True:
        imp3 = os.path.join(edipath3, station + ediext)
        implst.append(imp3)

    if implst == [] or len(implst) == 1:
        stationclst.remove(station)
        pass
    else:
        implst = [mtedi.Edi(implst[0]), mtedi.Edi(implst[1])]
        period = implst[0].period
        n = len(period)

        z1 = implst[0].Z.z
        z2 = implst[1].Z.z

        rpdict1 = implst[0].Z.resistivity
        rpdict2 = implst[1].Z.resistivity
        # compute static shift for each x and y component
        sx = np.sqrt(np.mean(rpdict1[0:10, 0, 1] / rpdict2[0:10, 0, 1]))
        sy = np.sqrt(np.mean(rpdict1[0:10, 1, 0] / rpdict2[0:10, 1, 0]))

        # remove static shift from 2nd set of files
        z2[:, 0, 0] = z2[:, 0, 0] * sx
        z2[:, 0, 1] = z2[:, 0, 1] * sx
        z2[:, 1, 0] = z2[:, 1, 0] * sy
        z2[:, 1, 1] = z2[:, 1, 1] * sy

        #        z1det=.2*period*abs(np.array([np.sqrt(np.linalg.det(zz)) for zz in z1]))**2
        #        z2det=.2*period*abs(np.array([np.sqrt(np.linalg.det(zz)) for zz in z2]))**2
        z1det = np.array([np.sqrt(abs(np.linalg.det(zz))) for zz in z1])
        z2det = np.array([np.sqrt(abs(np.linalg.det(zz))) for zz in z2])

        zdet = (abs(z1det - z2det) / z1det) * 100

        replst.append((abs(z1det - z2det) / z1det) * 100)

        #        dr1,dp1,zd1=implst[0].getResPhaseDet()
        #        dr2,dp2,zd2=implst[1].getResPhaseDet()
        #
        #        preplst.append((abs(dp1[0]-dp2[0])/dp1[0])*100)

        # ---Phase tensor determinant---
        ptdict1 = mtpt.PhaseTensor(z_object=implst[0].Z)
        ptdict2 = mtpt.PhaseTensor(z_object=implst[1].Z)

        ptd1 = np.array(
            [np.sqrt(np.linalg.det(pt1)) * (180 / np.pi) for pt1 in ptdict1.pt]
        )
        ptd2 = np.array(
            [np.sqrt(np.linalg.det(pt2)) * (180 / np.pi) for pt2 in ptdict2.pt]
        )
        ptlst.append((abs(ptd1 - ptd2) / ptd1) * 100)

        ptdet = (abs(ptd1 - ptd2) / ptd1) * 100

        for freq, zz, pp in zip(1.0 / period, zdet, ptdet):
            lines.append("{0:<12}{1:>12.2f}{2:>12.2f}\n".format(freq, zz, pp))

        rfid = file(os.path.join(sv_path, "{0}_repeat.txt".format(station)), "w")
        rfid.writelines(lines)
        rfid.close()

replst = np.rot90(np.array(replst), 3)
# preplst=np.rot90(np.array(preplst),3)
ptlst = np.rot90(np.array(ptlst), 3)


##===============================================================================
## Plot data
##===============================================================================
# plt.rcParams['font.size']=6
# plt.rcParams['figure.subplot.left']=.11
# plt.rcParams['figure.subplot.right']=.98
# plt.rcParams['figure.subplot.bottom']=.08
# plt.rcParams['figure.subplot.top']=.98
# plt.rcParams['figure.subplot.hspace']=.005
# plt.rcParams['figure.subplot.wspace']=.005
#
# ff=28
# xlimits=(-3,3)
# ylimits=(-2.4,1.75)
#
#
# emax=1
# fig=plt.figure(1,[14,14],dpi=300)
# ax1=fig.add_subplot(1,1,1,aspect='equal')
# for ss in range(ns):
#    eheightd=phimaxarr[ff,ss]/phimaxarr[ff,:].max()*esize
#    ewidthd=phiminarr[ff,ss]/phimaxarr[ff,:].max()*esize
#
#    if eheightd>emax or ewidthd>emax:
#        pass
#
#    else:
#        ellipd=Ellipse((lonlst[ss],latlst[ss]),
#                       width=ewidthd,
#                       height=eheightd,
#                       angle=azimutharr[ff,ss])
#        ellipd.set_facecolor((1,1-ecolorarr[ff,ss],.1))
#        ax1.add_artist(ellipd)
#
#
# ax1.set_xlim(xlimits)
# ax1.set_ylim(ylimits)
#
# ax1.text(xlimits[0]+.05,ylimits[1]-.1,'T={0:.2g}'.format(period[ff]),
#         verticalalignment='top',horizontalalignment='left',
#         fontdict={'size':8,'weight':'bold'})
# ax1.text(0,0,'X',
#         verticalalignment='center',
#         horizontalalignment='center',
#         fontdict={'size':9,'weight':'bold'})
# ellips=Ellipse((2.45,-2.),width=esize/2,
#               height=esize/2,angle=0)
# ellips.set_facecolor((.1,.1,1.))
# ax1.add_artist(ellips)
# ax1.grid(alpha=.2)
#
# ax1.text(2.45,-2.+esize/3.3,
#         '$\Delta$={0:.2g}'.format(esize/2*phimaxarr[ff].max()),
#         horizontalalignment='center',
#         verticalalignment='baseline')
#
# ax1.set_xlabel('easting (km)',fontdict={'size':9,'weight':'bold'})
# ax1.set_ylabel('northing (km)',fontdict={'size':9,'weight':'bold'})
# ax1.xaxis.set_minor_locator(MultipleLocator(.25))
# ax1.yaxis.set_minor_locator(MultipleLocator(.25))
#
##add colorbar
# cbax=make_axes(ax1,shrink=.40,orientation='horizontal')
# cbx=ColorbarBase(cbax[0],cmap=ptcmap,norm=Normalize(vmin=0,vmax=cmax*a),
#                orientation='horizontal',format='%.2g')
# cbx.set_label('(|$\Delta_{max}$|+|$\Delta_{min}$|)/2 ',
#                  fontdict={'size':7,'weight':'bold'})
# plt.show()
