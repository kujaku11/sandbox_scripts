# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 12:54:20 2016

@author: jpeacock
"""

import os
import matplotlib.pyplot as plt
import scipy.signal as sps
import mtpy.core.mt as mt
import numpy as np
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

base_path = r"c:\Users\jpeacock\Documents\ShanesBugs\Tongario_Hill\original"
post_path = r"c:\Users\jpeacock\Documents\ShanesBugs\Tongario_Hill\repeat"

edi_base_list = [
    os.path.join(base_path, edi)
    for edi in os.listdir(base_path)
    if edi.endswith(".edi")
]

edi_post_list = [
    os.path.join(post_path, edi)
    for edi in os.listdir(post_path)
    if edi.endswith(".edi")
]

# ==============================================================================
# parameters
# ==============================================================================
ns = len(edi_base_list)
nr = 2 * ns
nf = 40
ks = 11
pad = 3
comp_list = ["phimin", "phimax", "azimuth", "skew"]
limit_list = [(-3, 3), (-3, 3), (-5, 5), (-1, 1)]

# ==============================================================================
#
# ==============================================================================

base_arr = np.zeros(
    ns,
    dtype=[
        ("station", "|S10"),
        ("lat", np.float),
        ("lon", np.float),
        ("elev", np.float),
        ("rel_east", np.float),
        ("rel_north", np.float),
        ("east", np.float),
        ("north", np.float),
        ("zone", "|S4"),
        ("phimin", (np.float, (nf))),
        ("phimax", (np.float, (nf))),
        ("azimuth", (np.float, (nf))),
        ("skew", (np.float, (nf))),
    ],
)
# ,
#                               ('z_err', (np.complex, (nf, 2, 2))),
#                               ('tip', (np.complex, (nf, 1, 2))),
#                               ('tip_err', (np.complex, (nf, 1, 2)))])

post_arr = np.zeros(
    ns,
    dtype=[
        ("station", "|S10"),
        ("lat", np.float),
        ("lon", np.float),
        ("elev", np.float),
        ("rel_east", np.float),
        ("rel_north", np.float),
        ("east", np.float),
        ("north", np.float),
        ("zone", "|S4"),
        ("phimin", (np.float, (nf))),
        ("phimax", (np.float, (nf))),
        ("azimuth", (np.float, (nf))),
        ("skew", (np.float, (nf))),
    ],
)
#                               ('z', (np.complex, (nf, 2, 2))),
#                               ('z_err', (np.complex, (nf, 2, 2))),
#                               ('tip', (np.complex, (nf, 1, 2))),
#                               ('tip_err', (np.complex, (nf, 1, 2)))]
for ii, base_edi in enumerate(edi_base_list):
    mt_obj = mt.MT(base_edi)
    base_arr[ii]["station"] = mt_obj.station
    base_arr[ii]["lat"] = mt_obj.lat
    base_arr[ii]["lon"] = mt_obj.lon
    base_arr[ii]["elev"] = mt_obj.elev
    base_arr[ii]["north"] = mt_obj.north
    base_arr[ii]["east"] = mt_obj.east
    base_arr[ii]["zone"] = mt_obj.utm_zone
    base_arr[ii]["phimin"][:] = sps.medfilt(mt_obj.pt.phimin[0], kernel_size=ks)
    base_arr[ii]["phimax"][:] = sps.medfilt(mt_obj.pt.phimax[0], kernel_size=ks)
    base_arr[ii]["azimuth"][:] = sps.medfilt(mt_obj.pt.azimuth[0], kernel_size=ks)
    base_arr[ii]["skew"][:] = sps.medfilt(mt_obj.pt.beta[0], kernel_size=ks)

#    base_arr[ii]['z'][:, :, :] = mt_obj.Z.z
#    base_arr[ii]['z_err'][:, :, :] = mt_obj.Z.zerr
#    base_arr[ii]['tip'][:, :, :] = mt_obj.Tipper.tipper
#    base_arr[ii]['tip_err'][:, :, :] = mt_obj.Tipper.tippererr

for ii, post_edi in enumerate(edi_post_list):
    mt_obj = mt.MT(post_edi)
    post_arr[ii]["station"] = mt_obj.station
    post_arr[ii]["lat"] = mt_obj.lat
    post_arr[ii]["lon"] = mt_obj.lon
    post_arr[ii]["elev"] = mt_obj.elev
    post_arr[ii]["north"] = mt_obj.north
    post_arr[ii]["east"] = mt_obj.east
    post_arr[ii]["zone"] = mt_obj.utm_zone
    post_arr[ii]["phimin"][:] = sps.medfilt(mt_obj.pt.phimin[0], kernel_size=ks)
    post_arr[ii]["phimax"][:] = sps.medfilt(mt_obj.pt.phimax[0], kernel_size=ks)
    post_arr[ii]["azimuth"][:] = sps.medfilt(mt_obj.pt.azimuth[0], kernel_size=ks)
    post_arr[ii]["skew"][:] = sps.medfilt(mt_obj.pt.beta[0], kernel_size=ks)
#    post_arr[ii]['z'][:, :, :] = mt_obj.Z.z
#    post_arr[ii]['z_err'][:, :, :] = mt_obj.Z.zerr
#    post_arr[ii]['tip'][:, :, :] = mt_obj.Tipper.tipper
#    post_arr[ii]['tip_err'][:, :, :] = mt_obj.Tipper.tippererr

east_arr = np.array(sorted(base_arr["east"]))
north_arr = np.array(sorted(base_arr["north"]))
lat_arr = np.array(sorted(base_arr["lat"]))
lon_arr = np.array(sorted(base_arr["lon"]))

# x_arr = np.linspace(lon_arr.min(), lon_arr.max(), num=2*ns)
# y_arr = np.linspace(lat_arr.min(), lat_arr.max(), num=2*ns)
x_arr = np.linspace(east_arr.min(), east_arr.max(), num=nr)
y_arr = np.linspace(north_arr.min(), north_arr.max(), num=nr)

x, y = np.meshgrid(x_arr, y_arr)

f_arr = mt_obj.Z.freq.copy()


for ii, ff in enumerate(f_arr):
    fig = plt.figure(1, [6, 6], dpi=300)
    fig.clf()
    fig.subplots_adjust(
        left=0.1, right=0.95, top=0.9, bottom=0.1, hspace=0.2, wspace=0.15
    )

    for cc, comp, limits in zip(range(1, 5), comp_list, limit_list):
        test_arr = np.zeros((nr, nr))
        for b_arr in base_arr:
            for p_arr in post_arr:
                if b_arr["station"][-3:-1] == p_arr["station"][-3:-1]:
                    jj = np.where(x_arr >= b_arr["east"])[0][0]
                    kk = np.where(y_arr >= b_arr["north"])[0][0]
                    #                    test_arr[kk, :] += b_arr[comp][ii]-p_arr[comp][ii]
                    #                    test_arr[:, jj] += b_arr[comp][ii]-p_arr[comp][ii]
                    test_arr[
                        max([kk - pad, 0]) : min([kk + pad, nr]),
                        max([jj - pad, 0]) : min([jj + pad, nr]),
                    ] += (
                        b_arr[comp][ii] - p_arr[comp][ii]
                    )
                    continue

        ax = fig.add_subplot(2, 2, cc, aspect="equal")

        #        im = ax.imshow(sps.medfilt2d(test_arr, kernel_size=(5, 5)),
        #        im = ax.imshow(test_arr,
        #                       origin='lower',
        #                       extent=(lon_arr.min()*.99995, lon_arr.max()*1.00005,
        #                               lat_arr.min()*1.0001, lat_arr.max()*.99995),
        #                        vmin=limits[0],
        #                        vmax=limits[1],
        #                        cmap='jet')
        im = ax.pcolormesh(
            (x - x.mean()) / 1000.0,
            (y - y.mean()) / 1000.0,
            sps.medfilt2d(test_arr, kernel_size=(ks, ks)),
            vmin=limits[0],
            vmax=limits[1],
            cmap="jet_r",
        )
        plt.colorbar(im, ax=ax)

        for b_arr in base_arr:
            #            ax.scatter(b_arr['lon'], b_arr['lat'],
            #                       marker='v', s=20, c='k')
            ax.scatter(
                (b_arr["east"] - x.mean()) / 1000.0,
                (b_arr["north"] - y.mean()) / 1000.0,
                marker="v",
                s=20,
                c="k",
            )
        if cc == 3 or cc == 4:
            #            ax.set_xlabel('Longitude (deg)',
            #                          fontdict={'size':8, 'weight':'bold'})
            ax.set_xlabel("Easting (km)", fontdict={"size": 8, "weight": "bold"})
        if cc == 1 or cc == 3:
            #            ax.set_ylabel('Latitude(deg)',
            #                          fontdict={'size':8, 'weight':'bold'})
            ax.set_ylabel("Northing (km)", fontdict={"size": 8, "weight": "bold"})
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        #        ax.xaxis.set_major_locator(MultipleLocator(1000.))
        #        ax.yaxis.set_major_locator(MultipleLocator(1000.))
        ax.set_title(comp, {"size": 9, "weight": "bold"})
        ax.axis("tight")
    fig.suptitle(
        "Difference for {0:.5g} s".format(1.0 / ff),
        fontdict={"size": 10, "weight": "bold"},
    )
    plt.tight_layout()
    plt.show()
    fig.savefig(
        r"c:\Users\jpeacock\Documents\ShanesBugs\Tongario_Hill\plots\{0:02}_TNG_diff.png".format(
            ii
        ),
        dpi=300,
    )
