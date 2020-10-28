# -*- coding: utf-8 -*-
"""
Created on Wed May 25 16:39:30 2011

@author: a1185872

This script will plot phase tensor residuals.  The things that you need to 
change before you run are:
    
    edipathb,edipathi -> these are the paths to where the edi files for the
                       base survey and the post injection survey, respectively.
    
    pkfn -> is a pickle file to where all the calculated data is stored so 
            each time you run the program it won't have to calculate the 
            residual over again.  

The things you can change are:
    ctype = 'fm' for the the forward model, your edi files,
            or 'data' to plot the residuals from the Paralana data
    tensor_type = 'pt' to plot the phase tensor residuals
            'rt' to plot the resistivity tensor residuals
    plot_type = 'pseudo' to plot a pseudo section of the tensor residuals
                'map' to plot a map view of the tensor residuals
            
    for plotting you can change:
        prange = list of periods to plot
        xlimits = limits of the plot in the x-direction (only works for maps)
        ylimits = limits of the plot in the y-direction (km)
        esize = size of ellipses
        ecmax = maximum of the color, anything above will be colored red
"""

# ==============================================================================
import os
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sps
from matplotlib.colors import LinearSegmentedColormap, Normalize
import mtpy.core.edi as mtedi
import mtpy.analysis.pt as mtpt
import mtpy.utils.latlongutmconversion as utm2ll
from matplotlib.colorbar import *
from matplotlib.patches import Ellipse
import pickle

# ==============================================================================


# ==============================================================================
# Inputs
# ==============================================================================

plot_type = "pseudo"  # map of pseudo for map or pseudo section
diff_yn = "y"
line_dir = "ew"
borehole_loc = (139.72851, -30.2128)


bhz, bhe, bhn = utm2ll.LLtoUTM(23, borehole_loc[1], borehole_loc[0])

# ==============================================================================
# a few constants
# ==============================================================================

refe = 23
# phase tensor map
ptcmapdict = {
    "red": ((0.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
    "green": ((0.0, 0.0, 1.0), (1.0, 0.0, 1.0)),
    "blue": ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
}
ptcmap = LinearSegmentedColormap("ptcmap", ptcmapdict, 256)

# phase tensor map for difference (reverse)
ptcmapdictr = {
    "red": ((0.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
    "green": ((0.0, 1.0, 0.0), (1.0, 1.0, 0.0)),
    "blue": ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
}
ptcmapr = LinearSegmentedColormap("ptcmapr", ptcmapdictr, 256)

# resistivity tensor map for calculating delta
ptcmapdict2 = {
    "red": ((0.0, 0.0, 1.0), (1.0, 0.0, 1.0)),
    "green": ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
    "blue": ((0.0, 1.0, 0.0), (1.0, 1.0, 0.0)),
}
ptcmap2 = LinearSegmentedColormap("ptcmap2", ptcmapdict2, 256)

# resistivity tensor map for calcluating resistivity difference
rtcmapdict3 = {
    "red": ((0.0, 0.0, 0.0), (0.5, 1.0, 1.0), (1.0, 1.0, 0.0)),
    "green": ((0.0, 0.0, 0.0), (0.5, 1.0, 1.0), (1.0, 0.0, 0.0)),
    "blue": ((0.0, 0.0, 1.0), (0.5, 1.0, 1.0), (1.0, 0.0, 0.0)),
}
rtcmap3 = LinearSegmentedColormap("rtcmap3", rtcmapdict3, 256)

# resistivity tensor map for calcluating apparent resistivity
rtcmapdict3r = {
    "red": ((0.0, 1.0, 1.0), (0.5, 1.0, 1.0), (1.0, 0.0, 0.0)),
    "green": ((0.0, 0.0, 0.0), (0.5, 1.0, 1.0), (1.0, 0.0, 0.0)),
    "blue": ((0.0, 0.0, 0.0), (0.5, 1.0, 1.0), (1.0, 1.0, 1.0)),
}
rtcmap3r = LinearSegmentedColormap("rtcmap3r", rtcmapdict3r, 256)


ecmin = 0
# ===============================================================================
# Initialize parameters
# ===============================================================================

# set edipaths
edipathb = r"c:\Users\jpeacock-pr\Documents\Paralana\Base"
edipathi = r"c:\Users\jpeacock-pr\Documents\Paralana\Post"

# pickle file name
pkfn = r"c:\Users\jpeacock-pr\Documents\Paralana\PT_Residual_Paralana.pkl"

# make list of existing edifiles
if diff_yn == "y":
    edilst = [
        [os.path.join(edipathb, edib), os.path.join(edipathi, edii)]
        for edib in os.listdir(edipathb)
        for edii in os.listdir(edipathi)
        if edib.find(".") > 0
        if edib[0:4] == edii[0:4]
    ]
    mfs = (3, 5)
elif diff_yn == "n":
    edilst = [
        os.path.join(edipathi, edii)
        for edii in os.listdir(edipathi)
        if edii.find(".edi") > 0
    ]
    mfs = (1, 1)
a = 1
# number of frequencies
nf = 43
ns = len(edilst)
noise = None
# plot parameters
# -------MAP-----------------------
if plot_type == "map":
    prange = [18, 24, 28, 30, 33, 35]
    xlimits = (-3.4, 3.4)
    ylimits = (-2.4, 2.8)
    esize = 2
    if diff_yn == "y":
        ecmax = 0.25
        fignum = 10
    elif diff_yn == "n":
        ecmax = 0.25
        fignum = 11

# ------PSEUDO SECTION----------------------------
elif plot_type == "pseudo":
    esize = 1
    yspacing = 0.3
    ylimits = (-yspacing / 2, nf * (yspacing) + yspacing / 2)
    xstep = 1
    xscaling = 1
    ecmax = 0.25
    if line_dir == "ew":
        pstationlst = ["pb{0:}".format(ii) for ii in range(44, 33, -1)] + [
            "pb{0:}".format(ii) for ii in range(23, 34)
        ]
        # stationlst.remove('pb27')
        fignum = 14
    elif line_dir == "ns":
        pstationlst = (
            ["pb{0:}".format(ii) for ii in range(22, 11, -1)]
            + ["pb0{0:}".format(ii) for ii in range(1, 10)]
            + ["pb10", "pb11"]
        )
        pstationlst.remove("pb05")
        pstationlst.remove("pb06")
        pstationlst.remove("pb12")
        fignum = 15


# ==============================================================================
# Make a pickle file with all the data so you don't have to calculate each time
# ==============================================================================
if not os.path.isfile(pkfn):
    azimutharr = np.zeros((nf, ns))
    phimaxarr = np.zeros((nf, ns))
    phiminarr = np.zeros((nf, ns))
    betaarr = np.zeros((nf, ns))
    colorarr = np.zeros((nf, ns))

    latlst = np.zeros(ns)
    lonlst = np.zeros(ns)

    stationlst = []

    for ss, station in enumerate(edilst):
        # make a data type Z
        edi1 = mtedi.Edi(station[0])
        edi2 = mtedi.Edi(station[1])

        pt1 = mtpt.PhaseTensor(z_object=edi1.Z)
        pt2 = mtpt.PhaseTensor(z_object=edi2.Z)

        stationlst.append(edi1.station)

        sz, se, sn = utm2ll.LLtoUTM(refe, edi1.lat, edi1.lon)
        latlst[ss] = (sn - bhn) / 1000.0
        lonlst[ss] = (se - bhe) / 1000.0

        # calculate the difference between the two phase tensor ellipses
        for ii in range(nf):
            phi = np.eye(2) - (np.dot(np.linalg.inv(pt1.pt[ii]), pt2.pt[ii]))

            # compute the trace
            tr = phi[0, 0] + phi[1, 1]
            # Calculate skew of phi and the cooresponding error
            skew = phi[0, 1] - phi[1, 0]
            # calculate the determinate and determinate error of phi
            phidet = abs(np.linalg.det(phi))

            # calculate reverse trace and error
            revtr = phi[0, 0] - phi[1, 1]

            # calculate reverse skew and error
            revskew = phi[1, 0] + phi[0, 1]

            beta = 0.5 * np.arctan2(skew, tr) * (180 / np.pi)
            alpha = 0.5 * np.arctan2(revskew, revtr) * (180 / np.pi)

            # calculate azimuth
            azimuth = alpha - beta

            # calculate phimax
            phimax = np.sqrt(abs((0.5 * tr) ** 2 + (0.5 * skew) ** 2)) + np.sqrt(
                abs((0.5 * tr) ** 2 + (0.5 * skew) ** 2 - np.sqrt(phidet) ** 2)
            )

            # calculate minimum value for phi
            if phidet >= 0:
                phimin = np.sqrt(abs((0.5 * tr) ** 2 + (0.5 * skew) ** 2)) - np.sqrt(
                    abs((0.5 * tr) ** 2 + (0.5 * skew) ** 2 - np.sqrt(phidet) ** 2)
                )
            elif phidet < 0:
                phimin = -1 * np.sqrt(
                    abs((0.5 * tr) ** 2 + (0.5 * skew) ** 2)
                ) - np.sqrt(
                    abs((0.5 * tr) ** 2 + (0.5 * skew) ** 2 - (np.sqrt(phidet)) ** 2)
                )

            # set the color of the array as the geometric mean of the
            ecolor = np.sqrt(abs(phimin) * abs(phimax))

            # put things into arrays
            phimaxarr[ii, ss] = phimax
            phiminarr[ii, ss] = phimin
            azimutharr[ii, ss] = azimuth
            betaarr[ii, ss] = abs(beta)
            colorarr[ii, ss] = ecolor

    # ===============================================================================
    # Filter the arrays if desired
    # ===============================================================================
    phimaxarr = sps.medfilt2d(phimaxarr, kernel_size=mfs)
    phiminarr = sps.medfilt2d(phiminarr, kernel_size=mfs)
    azimutharr = sps.medfilt2d(azimutharr, kernel_size=mfs)
    betaarr = sps.medfilt2d(betaarr, kernel_size=mfs)
    colorarr = sps.medfilt2d(colorarr, kernel_size=mfs)

    # ===============================================================================
    # Pickle results so don't have to reload them everytime
    # ===============================================================================
    fid = file(pkfn, "w")
    pickle.dump(
        (
            phimaxarr,
            phiminarr,
            azimutharr,
            betaarr,
            colorarr,
            latlst,
            lonlst,
            stationlst,
            edi1.period,
        ),
        fid,
    )
    fid.close()

# ==============================================================================
# Print what you are plotting
# ==============================================================================
print "pkfn:\t", pkfn
print "Plotting:\t", plot_type

# ===============================================================================
# Plot ellipses in map view
# ===============================================================================

# load pickled file
pkfid = file(pkfn, "r")
(
    phimaxarr,
    phiminarr,
    azimutharr,
    betarr,
    ecolorarr,
    latlst,
    lonlst,
    stationlst,
    period,
) = pickle.load(pkfid)
pkfid.close()

print "ecolorarr.max()= {0:.5f}".format(ecolorarr.max())

if plot_type == "map":

    ecolorarr = np.nan_to_num(ecolorarr)
    nrows = len(prange) / ncols

    plt.rcParams["font.size"] = 6
    plt.rcParams["figure.subplot.left"] = 0.1
    plt.rcParams["figure.subplot.right"] = 0.92
    plt.rcParams["figure.subplot.bottom"] = 0.08
    plt.rcParams["figure.subplot.top"] = 0.95
    plt.rcParams["figure.subplot.hspace"] = 0.005
    plt.rcParams["figure.subplot.wspace"] = 0.005

    emax = 2 * esize
    fig = plt.figure(fignum, [14, 14], dpi=300)
    plt.clf()
    for ii, ff in enumerate(prange, 1):
        ax1 = fig.add_subplot(nrows, ncols, ii, aspect="equal")
        for ss in range(ns):
            if ctype == "data":
                eheightd = phiminarr[ff, ss] / (np.median(phimaxarr[ff, :]) * 3) * esize
                ewidthd = phimaxarr[ff, ss] / (np.median(phimaxarr[ff, :]) * 3) * esize
            else:
                eheightd = phiminarr[ff, ss] / phimaxarr[ff, :].max() * esize
                ewidthd = phimaxarr[ff, ss] / phimaxarr[ff, :].max() * esize

            if eheightd > emax or ewidthd > emax:
                pass

            else:
                if diff_yn == "y":
                    ellipd = Ellipse(
                        (lonlst[ss], latlst[ss]),
                        width=ewidthd,
                        height=eheightd,
                        angle=azimutharr[ff, ss] - 90,
                    )
                elif diff_yn == "n":
                    ellipd = Ellipse(
                        (lonlst[ss], latlst[ss]),
                        width=ewidthd,
                        height=eheightd,
                        angle=azimutharr[ff, ss],
                    )
            # color ellipse
            if tensor_type == "pt":
                if diff_yn == "y":
                    cvar = ecolorarr[ff, ss] / ecmax
                elif diff_yn == "n":
                    cvar = ecolorarr[ff, ss] / 90
                if abs(cvar) > 1:
                    ellipd.set_facecolor((1, 0, 0.1))
                else:
                    ellipd.set_facecolor((1, 1 - abs(cvar), 0.1))
            elif tensor_type == "rt":
                if diff_yn == "y":
                    cvar = betarr[ff, ss] / ecmax
                    if cvar < 0:
                        if cvar < -1:
                            ellipd.set_facecolor((0, 0, 1))
                        else:
                            ellipd.set_facecolor((1 - abs(cvar), 1 - abs(cvar), 1))
                    else:
                        if cvar > 1:
                            ellipd.set_facecolor((1, 0, 0))
                        else:
                            ellipd.set_facecolor((1, 1 - abs(cvar), 1 - abs(cvar)))
                elif diff_yn == "n":
                    cvar = (ecolorarr[ff, ss] - ecmin) / (ecmax - ecmin)
                    if cvar > 0.5:
                        if cvar > 1:
                            ellipd.set_facecolor((0, 0, 1))
                        else:
                            ellipd.set_facecolor((1 - abs(cvar), 1 - abs(cvar), 1))
                    else:
                        if cvar < -1:
                            ellipd.set_facecolor((1, 0, 0))
                        else:
                            ellipd.set_facecolor((1, 1 - abs(cvar), 1 - abs(cvar)))
            ax1.add_patch(ellipd)

        ax1.set_xlim(xlimits)
        ax1.set_ylim(ylimits)

        ax1.text(
            xlimits[0] + 0.20,
            ylimits[1] - 0.2,
            "T={0:.2g} s".format(period[ff]),
            verticalalignment="top",
            horizontalalignment="left",
            fontdict={"size": 8, "weight": "bold"},
            bbox={"facecolor": "white"},
        )
        ax1.text(
            0,
            0,
            "X",
            verticalalignment="center",
            horizontalalignment="center",
            fontdict={"size": 9, "weight": "bold"},
        )
        ellips = Ellipse(
            (xlimits[0] + 0.85, ylimits[0] + 0.65), width=1, height=1, angle=0
        )
        ellips.set_facecolor((0.1, 0.1, 0.1))
        ax1.add_artist(ellips)
        ax1.grid(alpha=0.2)

        if ctype == "fm":
            ax1.text(
                xlimits[0] + 0.20,
                ylimits[0] + 1.4,
                "$\Delta$={0:.2g}".format(phimaxarr[ff, :].max() * a),
                horizontalalignment="left",
                verticalalignment="bottom",
                bbox={"facecolor": "white"},
            )
        elif ctype == "data":
            ax1.text(
                xlimits[0] + 0.20,
                ylimits[0] + 1.4,
                "$\Delta$={0:.2g}".format(np.median(phimaxarr[ff, :]) * 3),
                horizontalalignment="left",
                verticalalignment="bottom",
                bbox={"facecolor": "white"},
            )

        if ii > nrows:
            ax1.set_xlabel("easting (km)", fontdict={"size": 9, "weight": "bold"})
        if ii < (nrows - 1) * ncols + 1:
            ax1.xaxis.set_ticklabels(
                ["" for hh in range(len(ax1.xaxis.get_ticklabels()))]
            )

        if ii == 1 or ii == ncols + 1 or ii == 2 * ncols + 1 or ii == 3 * ncols + 1:
            pass
        else:
            ax1.yaxis.set_ticklabels(
                ["" for hh in range(len(ax1.yaxis.get_ticklabels()))]
            )
        if ii == ncols * int(nrows / 2) + 1 or ii == 1:
            ax1.set_ylabel("northing (km)", fontdict={"size": 9, "weight": "bold"})

    # add colorbar
    ax2 = fig.add_subplot(1, 1, 1)
    ax2.set_visible(False)
    cbax = make_axes(ax2, shrink=0.99, fraction=0.015, pad=10.2)
    if tensor_type == "rt":
        if diff_yn == "y":
            cbx = ColorbarBase(
                cbax[0],
                cmap=rtcmap3,
                norm=Normalize(vmin=-ecmax, vmax=ecmax),
                orientation="vertical",
                format="%.2g",
            )
            cbx.set_label(
                "App. Res. ($\Omega \cdot$m) ", fontdict={"size": 7, "weight": "bold"}
            )
        if diff_yn == "n":
            cbx = ColorbarBase(
                cbax[0],
                cmap=rtcmap3r,
                norm=Normalize(vmin=ecmin, vmax=ecmax),
                orientation="vertical",
                format="%.2g",
            )
            cbx.set_label(
                "App. Res. ($\Omega \cdot$m) ", fontdict={"size": 7, "weight": "bold"}
            )

    elif tensor_type == "pt":
        if diff_yn == "y":
            cbx = ColorbarBase(
                cbax[0],
                cmap=ptcmap,
                norm=Normalize(vmin=0, vmax=ecmax),
                orientation="vertical",
            )
            cbx.set_label(
                "(|$\Delta_{max}$|+|$\Delta_{min}$|)/2 ",
                fontdict={"size": 7, "weight": "bold"},
            )
        elif diff_yn == "n":
            cbx = ColorbarBase(
                cbax[0],
                cmap=ptcmap,
                norm=Normalize(vmin=0, vmax=90),
                orientation="vertical",
            )
            cbx.set_label("Phimin (deg) ", fontdict={"size": 7, "weight": "bold"})

    ####----Make scale ellipse
    rect = Rectangle((xlimits[1] - 0.2, 0), 0.5, 0.5)
    rect.set_facecolor((1, 1, 1))
    rect.set_edgecolor((1, 1, 1))
    ax1.add_artist(rect)

    ax1.text(
        xlimits[1] - 0.12,
        0.5,
        "$\Delta = 0.15$",
        fontdict={"size": 8},
        horizontalalignment="center",
        verticalalignment="baseline",
        bbox={"facecolor": "white", "edgecolor": "white"},
    )

    ellips = Ellipse((xlimits[1] - 0.1, esize * 2), width=esize, height=esize, angle=0)
    ellips.set_facecolor((0.1, 0.1, 1.0))
    ax1.add_artist(ellips)

    plt.show()


# ==============================================================================
# Plot Data Pseudo section
# ==============================================================================

elif plot_type == "pseudo":
    sdict = dict([(station[0:4], ii) for ii, station in enumerate(stationlst)])

    pslst = []
    xlabels = []
    offsetlst = []
    for pss in pstationlst:
        try:
            pslst.append(sdict[pss])
            xlabels.append(pss[2:4])
            if line_dir == "ew":
                offsetlst.append(lonlst[sdict[pss]])
            elif line_dir == "ns":
                offsetlst.append(latlst[sdict[pss]])
        except KeyError:
            pass

    nx = len(xlabels)
    xtks = list(offsetlst)
    xtks.sort()
    xtks = np.array(xtks)
    plt.rcParams["font.size"] = 8
    plt.rcParams["figure.subplot.left"] = 0.1
    plt.rcParams["figure.subplot.right"] = 0.94
    plt.rcParams["figure.subplot.bottom"] = 0.08
    plt.rcParams["figure.subplot.top"] = 0.95
    plt.rcParams["figure.subplot.hspace"] = 0.05

    emax = 5 * esize
    # create a plot instance
    fig = plt.figure(fignum, [8, 6], dpi=300)
    plt.clf()
    ax1 = fig.add_subplot(1, 1, 1, aspect="equal")

    for jj, ss in enumerate(pslst):
        for ff in range(nf):
            eheightd = phiminarr[ff, ss] / (np.median(phimaxarr[:, :]) * 3) * esize
            ewidthd = phimaxarr[ff, ss] / (np.median(phimaxarr[:, :]) * 3) * esize

            if eheightd > emax or ewidthd > emax:
                pass
            else:
                ellipd = Ellipse(
                    (lonlst[ss] * xscaling, yspacing * (nf - ff)),
                    width=ewidthd,
                    height=eheightd,
                    angle=azimutharr[ff, ss] - 90,
                )

            # color ellipse
            if diff_yn == "y":
                cvar = ecolorarr[ff, ss] / ecmax
            elif diff_yn == "n":
                cvar = ecolorarr[ff, ss] / ecmax
            if abs(cvar) > 1:
                ellipd.set_facecolor((1, 0, 0.1))
            else:
                ellipd.set_facecolor((1, 1 - abs(cvar), 0.1))

            ax1.add_artist(ellipd)

    yticklabels = []
    for yy in np.arange(start=1, stop=nf + 1, step=2):
        if period[nf - yy] < 100:
            yticklabels.append("{0:.3g}".format(period[nf - yy]))
        else:
            yticklabels.append("{0:.0f}".format(period[nf - yy]))
    #    yticklabels=['%2.3g' % period[nf-ii] for ii in np.arange(start = 1,stop = nf+1,
    #                 step = 2)]
    ax1.set_ylabel("period (s)", fontdict={"size": 9, "weight": "bold"})
    ax1.set_yticks(np.arange(start=yspacing, stop=yspacing * nf + 1, step=2 * yspacing))
    ax1.set_yticklabels(yticklabels)

    # ax1.xaxis.set_tick_params(labelbottom='on',labeltop='on')

    ax1.set_xticks(xtks[range(0, nx, xstep)])
    # ax1.xaxis.set_ticklabels(['{0:.2g}'.format(nn) for nn in xtks[range(0,nx+1,2)]])
    ax1.set_xticklabels([xlabels[xx] for xx in range(0, nx, xstep)])
    ax1.set_xlim(min(offsetlst) - 0.5, max(offsetlst) + 0.5)
    ax1.set_ylim(ylimits)
    ax1.set_xlabel("station", fontdict={"size": 10, "weight": "bold"})
    # ax1.set_title('Before and After Injection',fontdict={'size':12,'weight':'bold'})
    ax1.grid()

    ax4 = make_axes(ax1, shrink=0.5, fraction=0.1, orientation="vertical", pad=0.005)
    if diff_yn == "y":
        cb1 = ColorbarBase(
            ax4[0],
            cmap=ptcmap,
            norm=Normalize(vmin=0, vmax=ecmax),
            orientation="vertical",
        )
    elif diff_yn == "n":
        cb1 = ColorbarBase(
            ax4[0],
            cmap=ptcmap,
            norm=Normalize(vmin=0, vmax=ecmax),
            orientation="vertical",
        )
    #        cb1.set_label('(|$\Delta_{max}$|+|$\Delta_{min}$|)/2')
    cb1.set_label("$\sqrt{\Delta \Phi_{max} \, \Delta \Phi_{min}}$")

    ####----Make scale ellipse
    rect = Rectangle((lonlst[-1] * 0.95, -yspacing / 2), 2, 3 * yspacing)
    rect.set_facecolor((1, 1, 1))
    rect.set_edgecolor((1, 1, 1))
    ax1.add_artist(rect)

    ax1.text(
        lonlst[-1] * 0.85,
        yspacing * 2.3,
        "$\Delta = 0.15$",
        fontdict={"size": 8},
        horizontalalignment="center",
        verticalalignment="baseline",
        bbox={"facecolor": "white", "edgecolor": "white"},
    )

    ellips = Ellipse((lonlst[-1] * 0.90, yspacing), width=esize, height=esize, angle=0)
    ellips.set_facecolor((0.1, 0.1, 1.0))
    ax1.add_artist(ellips)

    # plt.savefig(os.path.join(savepath,station+'PhaseTensorsComparison.png'))
    # plt.close()
    plt.show()
