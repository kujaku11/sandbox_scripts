# -*- coding: utf-8 -*-
"""
Created on Fri May 06 16:36:35 2016

@author: jpeacock
"""

import os
import scipy.signal as sps
import mtpy.core.mt as mt
import numpy as np
import pickle

# import mtpy.analysis.pt as mtpt
# import mtpy.imaging.mtplot as mtplot
import mtpy.imaging.mtplottools as mtplt

import matplotlib.pyplot as plt

# from matplotlib.ticker import MultipleLocator, FormatStrFormatter
# import matplotlib.patches as patches
# import mtpy.imaging.mtcolors as mtcl


class Data_array(object):
    """
    Fill a data array with information from a list of .edi files
    """

    def __init__(self, edi_list=None, edi_path=None, **kwargs):
        self.edi_list = edi_list
        self.edi_path = edi_path
        self.ns = None
        self.freq = None
        self.mt_obj_list = None
        self.ks = 1
        self.pickle_fn = None

        if self.edi_path is not None:
            self.get_edi_list()

        self.num_freq = kwargs.pop("num_freq", 24)

        self.data_type = [
            ("station", "|S10"),
            ("lat", np.float),
            ("lon", np.float),
            ("elev", np.float),
            ("rel_east", np.float),
            ("rel_north", np.float),
            ("east", np.float),
            ("north", np.float),
            ("zone", "|S4"),
            ("phimin", (np.float, (self.num_freq))),
            ("phimax", (np.float, (self.num_freq))),
            ("azimuth", (np.float, (self.num_freq))),
            ("skew", (np.float, (self.num_freq))),
            ("z", (np.complex, (self.num_freq, 2, 2))),
            ("z_err", (np.complex, (self.num_freq, 2, 2))),
            ("tip", (np.complex, (self.num_freq, 1, 2))),
            ("tip_err", (np.complex, (self.num_freq, 1, 2))),
        ]

        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

    def get_edi_list(self):
        """
        get edi_list from edi_path
        """

        if self.edi_path is not None:
            self.edi_list = [
                os.path.join(self.edi_path, edi)
                for edi in os.listdir(self.edi_path)
                if edi.endswith(".edi")
            ]
            self.ns = len(self.edi_list)
        else:
            raise IOError("Need to input a path to .edi files")

    def make_data_type(self):
        self.data_type = [
            ("station", "|S10"),
            ("lat", np.float),
            ("lon", np.float),
            ("elev", np.float),
            ("rel_east", np.float),
            ("rel_north", np.float),
            ("east", np.float),
            ("north", np.float),
            ("zone", "|S4"),
            ("freq", (np.float, (self.num_freq))),
            ("phimin", (np.float, (self.num_freq))),
            ("phimax", (np.float, (self.num_freq))),
            ("azimuth", (np.float, (self.num_freq))),
            ("skew", (np.float, (self.num_freq))),
            ("phimin_err", (np.float, (self.num_freq))),
            ("phimax_err", (np.float, (self.num_freq))),
            ("azimuth_err", (np.float, (self.num_freq))),
            ("skew_err", (np.float, (self.num_freq))),
            ("z", (np.complex, (self.num_freq, 2, 2))),
            ("z_err", (np.complex, (self.num_freq, 2, 2))),
            ("tip", (np.complex, (self.num_freq, 1, 2))),
            ("tip_err", (np.complex, (self.num_freq, 1, 2))),
        ]

    def get_freq(self):
        """
        get a list of frequencies, if not all stations have the same
        frequencies get a common group to interpolate on to.
        """
        if self.edi_list is None:
            self.get_edi_list()

        self.mt_obj_list = []
        freq_list = []
        nf_list = np.zeros(self.ns)
        for ii, edi in enumerate(self.edi_list):
            mt_obj = mt.MT(edi)
            self.mt_obj_list.append(mt_obj)
            freq_list.extend(list(mt_obj.Z.freq))
            nf_list[ii] = mt_obj.Z.freq.size

        frequencies = np.array(sorted(list(set(freq_list)), reverse=True))

        if nf_list.mean() != frequencies.size:
            interp_frequencies = np.logspace(
                np.log10(frequencies.min()),
                np.log10(frequencies.max()),
                num=nf_list.mean(),
            )

            print "interpolating data"
            for mt_obj in self.mt_obj_list:
                new_z, new_t = mt_obj.interpolate(interp_frequencies)
                mt_obj.Z = new_z
                mt_obj.Tipper = new_t

            self.freq = interp_frequencies

        else:
            self.freq = frequencies

        self.num_freq = self.freq.size

    def fill_data_array(self):
        """
        fill data according to dtype
        """
        if self.edi_list is None:
            self.get_edi_list()

        try:
            self.ns = len(self.edi_list)
        except TypeError:
            raise IOError("Length of edi_list is None, check edi_list")

        self.get_freq()
        self.make_data_type()

        self.data_array = np.zeros(self.ns, dtype=self.data_type)

        for ii, mt_obj in enumerate(self.mt_obj_list):
            self.data_array[ii]["station"] = mt_obj.station
            self.data_array[ii]["lat"] = mt_obj.lat
            self.data_array[ii]["lon"] = mt_obj.lon
            self.data_array[ii]["elev"] = mt_obj.elev
            self.data_array[ii]["north"] = mt_obj.north
            self.data_array[ii]["east"] = mt_obj.east
            self.data_array[ii]["zone"] = mt_obj.utm_zone
            self.data_array[ii]["freq"][:] = self.freq
            self.data_array[ii]["phimin"][:] = sps.medfilt(
                mt_obj.pt.phimin[0], kernel_size=self.ks
            )
            self.data_array[ii]["phimax"][:] = sps.medfilt(
                mt_obj.pt.phimax[0], kernel_size=self.ks
            )
            self.data_array[ii]["azimuth"][:] = sps.medfilt(
                mt_obj.pt.azimuth[0], kernel_size=self.ks
            )
            self.data_array[ii]["skew"][:] = sps.medfilt(
                mt_obj.pt.beta[0], kernel_size=self.ks
            )
            self.data_array[ii]["phimin_err"][:] = sps.medfilt(
                mt_obj.pt.phimin[1], kernel_size=self.ks
            )
            self.data_array[ii]["phimax_err"][:] = sps.medfilt(
                mt_obj.pt.phimax[1], kernel_size=self.ks
            )
            self.data_array[ii]["azimuth_err"][:] = sps.medfilt(
                mt_obj.pt.azimuth[1], kernel_size=self.ks
            )
            self.data_array[ii]["skew_err"][:] = sps.medfilt(
                mt_obj.pt.beta[1], kernel_size=self.ks
            )
            for kk in range(2):
                for ll in range(2):
                    self.data_array[ii]["z"][:, kk, ll] = (
                        sps.medfilt(mt_obj.Z.z[:, kk, ll].real, kernel_size=self.ks)
                        + sps.medfilt(mt_obj.Z.z[:, kk, ll].imag, kernel_size=self.ks)
                        * 1j
                    )
                    self.data_array[ii]["z_err"][:, kk, ll] = sps.medfilt(
                        mt_obj.Z.zerr[:, kk, ll], kernel_size=self.ks
                    )
            for nn in range(2):
                self.data_array[ii]["tip"][:, 0, nn] = (
                    sps.medfilt(
                        mt_obj.Tipper.tipper[:, 0, nn].real, kernel_size=self.ks
                    )
                    + sps.medfilt(
                        mt_obj.Tipper.tipper[:, 0, nn].imag, kernel_size=self.ks
                    )
                    * 1j
                )
                self.data_array[ii]["tip_err"][:, 0, nn] = sps.medfilt(
                    mt_obj.Tipper.tippererr[:, 0, nn], kernel_size=self.ks
                )

    def write_pickle_data(self, pickle_fn=None):
        """
        pickle the data to use lated
        """
        if pickle_fn is None and self.pickle_fn is None:
            if self.edi_path is not None:
                self.pickle_fn = os.path.join(self.edi_path, "Data.pkl")
            else:
                self.pickle_fn = os.path.join(
                    os.path.dirname(self.edi_list[0]), "Data.pkl"
                )
        else:
            self.pickle_fn = pickle_fn

        with open(self.pickle_fn, "w") as fid:
            pickle.dump(self.data_array, fid)

        print "Pickled file to {0}".format(self.pickle_fn)

    def load_pickle_data(self, pickle_fn=None):
        """
        load in pickled data
        """

        if pickle_fn is not None:
            self.pickle_fn = pickle_fn
        if self.pickle_fn is None:
            raise IOError("Need to input a file name for pickled data")

        if not os.path.isfile(self.pickle_fn):
            raise IOError("Could not find {0}, check path".format(self.pickle_fn))

        with open(self.pickle_fn, "r") as fid:
            self.data_array = pickle.load(fid)
            self.num_freq = self.data_array[0]["freq"].size


# ==============================================================================
# Test
# ==============================================================================
base_path = r"c:\Users\jpeacock\Documents\ShanesBugs\Tongario_Hill\original"
post_path = r"c:\Users\jpeacock\Documents\ShanesBugs\Tongario_Hill\repeat"

kernel_size = 1

base_pk_fn = os.path.join(base_path, "base_data_ks{0}.pkl".format(kernel_size))
post_pk_fn = os.path.join(post_path, "post_data_ks{0}.pkl".format(kernel_size))


replace_file = False
if replace_file == True:
    os.remove(base_pk_fn)
    os.remove(post_pk_fn)

if os.path.exists(base_pk_fn) is False:
    base_data = Data_array(edi_path=base_path)
    base_data.ks = kernel_size
    base_data.fill_data_array()
    base_data.write_pickle_data(pickle_fn=base_pk_fn)

if os.path.exists(post_pk_fn) is False:
    post_data = Data_array(edi_path=post_path)
    post_data.ks = kernel_size
    post_data.fill_data_array()
    post_data.write_pickle_data(pickle_fn=post_pk_fn)


base_data = Data_array()
base_data.load_pickle_data(base_pk_fn)

post_data = Data_array()
post_data.load_pickle_data(post_pk_fn)

s_list = base_data.data_array["station"]
ks = 9
for ss in s_list:
    b_arr = base_data.data_array[np.where(base_data.data_array["station"] == ss)[0][0]]
    p_arr = post_data.data_array[np.where(post_data.data_array["station"] == ss)[0][0]]
    fig = plt.figure(kernel_size, [12, 8])
    fig.clf()
    ax = fig.add_subplot(1, 1, 1)

    #    l1 = mtplt.plot_errorbar(ax,
    #                              1./b_arr['freq'],
    #                              sps.medfilt(b_arr['phimin']-p_arr['phimin'],
    #                                          ks),
    #                              y_error=sps.medfilt(b_arr['phimin_err']+p_arr['phimin_err'],
    #                                                  ks),
    #                              color=(0, 0, .85),
    #                              marker='s',
    #                              ms=5)
    #
    #    l2 = mtplt.plot_errorbar(ax,
    #                              1./b_arr['freq'],
    #                              sps.medfilt(b_arr['phimax']-p_arr['phimax'],
    #                                          ks),
    #                              y_error=sps.medfilt(b_arr['phimax_err']+p_arr['phimax_err'],
    #                                                  ks),
    #                              color=(0.85, 0, 0),
    #                              marker='s',
    #                              ms=5)
    #    l3 = mtplt.plot_errorbar(ax,
    #                              1./b_arr['freq'],
    #                              sps.medfilt(b_arr['skew']-p_arr['skew'],
    #                                          ks),
    #                              y_error=sps.medfilt(b_arr['skew_err']+p_arr['skew_err'],
    #                                                  ks),
    #                              color=(0, 0.85, 0),
    #                              marker='s',
    #                              ms=5)
    #    l4 = mtplt.plot_errorbar(ax,
    #                              1./b_arr['freq'],
    #                              sps.medfilt(b_arr['azimuth']-p_arr['azimuth'],
    #                                          ks),
    #                              y_error=b_arr['azimuth_err']+p_arr['azimuth_err'],
    #                              color=(0.85, 0.85, 0),
    #                              marker='s',
    #                              ms=5)
    l1 = mtplt.plot_errorbar(
        ax,
        1.0 / b_arr["freq"],
        b_arr["phimin"],
        y_error=b_arr["phimin_err"],
        color="k",
        marker="s",
        ms=5,
    )
    l2 = mtplt.plot_errorbar(
        ax,
        1.0 / p_arr["freq"],
        p_arr["phimin"],
        y_error=p_arr["phimin_err"],
        color=(0, 0, 0.85),
        marker="v",
        ms=5,
    )

    l3 = mtplt.plot_errorbar(
        ax,
        1.0 / b_arr["freq"],
        b_arr["phimax"],
        y_error=b_arr["phimax_err"],
        color="k",
        marker="s",
        ms=5,
    )
    l4 = mtplt.plot_errorbar(
        ax,
        1.0 / p_arr["freq"],
        p_arr["phimax"],
        y_error=p_arr["phimax_err"],
        color=(0.85, 0, 0),
        marker="v",
        ms=5,
    )

    l5 = mtplt.plot_errorbar(
        ax,
        1.0 / b_arr["freq"],
        b_arr["skew"],
        y_error=b_arr["skew_err"],
        color="k",
        marker="s",
        ms=5,
    )
    l6 = mtplt.plot_errorbar(
        ax,
        1.0 / p_arr["freq"],
        p_arr["skew"],
        y_error=p_arr["skew_err"],
        color=(0, 0.85, 0),
        marker="v",
        ms=5,
    )

    ax.legend(
        [l1[0], l2[0], l3[0], l4[0], l5[0], l6[0]],
        ["b_min", "p_min", "b_max", "p_max", "s_min", "s_max"],
        loc="lower left",
        ncol=3,
    )
    #    ax.legend([l1[0], l2[0], l3[0], l4[0]],
    #              ['phimin', 'phimax', 'skew', 'azimuth'],
    #              loc='lower left')

    ax.set_xlabel("Period")
    ax.set_xlim(
        (
            10 ** (np.floor(np.log10(1.0 / p_arr["freq"].max()))),
            10 ** (np.floor(np.log10(1.0 / p_arr["freq"].min()))),
        )
    )
    ax.set_xscale("log")

    ax.set_ylabel("Angle (deg)")
    ax.set_ylim(-5, 90)
    # ax.axis('tight')
    ax.grid("both", color=(0.75, 0.75, 0.75), lw=0.75)
    plt.tight_layout()

    fig.savefig(
        r"c:\Users\jpeacock\Documents\ShanesBugs\Tongario_Hill\plots_compare_diff\{0}.png".format(
            b_arr["station"]
        ),
        dpi=300,
        bbox_inches="tight",
    )

    print "Saved figure for station {0} {1}".format(b_arr["station"], p_arr["station"])
    plt.close("all")
