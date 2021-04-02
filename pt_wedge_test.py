# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 12:06:03 2019

@author: jpeacock
"""
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Ellipse
from matplotlib import colors
from matplotlib import colorbar
from mtpy.core import edi_collection
from mtpy.imaging import mtplottools as mtpl

from mtpy.imaging import mtcolors
import glob


class PlotPTShapes(mtpl.PlotSettings):
    """
    plot phase tensor ellipses and lines
    """

    def __init__(self, fn_list=None, **kwargs):
        super(PlotPTShapes, self).__init__(**kwargs)
        if fn_list is not None:
            self.mt_collection = edi_collection.EdiCollection(edilist=fn_list)

        self.plot_freq = 1.0
        self.wedge_width = 5.0
        self.phimax_cmap = "mt_rd2wh2bl_r"
        self.phimin_cmap = "mt_rd2wh2bl_r"
        self.gm_cmap = "mt_rd2wh2bl_r"
        self.skew_cmap = "Greys"
        self.phase_limits = (0, 90)
        self.skew_limits = (0, 9)
        self.skew_step = 3
        self.skew_lw = 4
        self.ellipse_alpha = 0.85
        self.y_limits = None
        self.map_scale = "ll"
        self.set_parameters_for_mapscale()

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.fig = None

    def set_parameters_for_mapscale(self):
        """
        try to scale things correctly
        """
        # set default size to 2
        if self.map_scale in ["deg", "latlon", "ll"]:
            self.ellipse_size = 0.05
            self.arrow_size = 0.05

        elif self.map_scale == "m":
            self.ellipse_size = 500.0
            self.arrow_size = 500.0

        elif self.map_scale == "km":
            self.ellipse_size = 0.5
            self.arrow_size = 0.5

        self.arrow_head_length = 0.25 * self.arrow_size
        self.arrow_head_width = 0.25 * self.arrow_size
        self.arrow_lw = 0.05 * self.arrow_size
        self.xpad = max([self.arrow_size, self.ellipse_size])
        self.ypad = max([self.arrow_size, self.ellipse_size])

    def get_pt_list(self):
        """
        get pt list
        """
        return self.mt_collection.get_phase_tensor_tippers(self.plot_freq)

    def plot(self):
        """
        plot pts
        """
        if self.fig is None:
            self.fig = plt.figure(self.fig_num, self.fig_size)
        self.fig.clf()

        self.ax = self.fig.add_subplot(1, 1, 1, aspect="equal")

        # get pt_dict
        for pt_dict in self.get_pt_list():
            self.add_pt_patch(pt_dict)

        self.get_axis_limits()
        self.set_axis_limits(self.x_limits, self.y_limits)

        self.set_axis_labels("Latitude (deg)", "Longitude (km)")

        self.fig.show()

    def redraw_plot(self):
        if self.fig is not None:
            self.fig.clf()
        self.plot()

    def add_pt_patch(self, pt_dict):
        """
        Add patches to plot
        """

        plot_x = pt_dict["lon"]
        plot_y = pt_dict["lat"]
        w1 = Wedge(
            (plot_x, plot_y),
            self.ellipse_size,
            90 - pt_dict["azimuth"] - self.wedge_width,
            90 - pt_dict["azimuth"] + self.wedge_width,
            color=mtcolors.get_plot_color(
                pt_dict["phi_max"],
                "phimax",
                self.phimax_cmap,
                self.phase_limits[0],
                self.phase_limits[1],
            ),
        )
        w2 = Wedge(
            (plot_x, plot_y),
            self.ellipse_size,
            270 - pt_dict["azimuth"] - self.wedge_width,
            270 - pt_dict["azimuth"] + self.wedge_width,
            color=mtcolors.get_plot_color(
                pt_dict["phi_max"],
                "phimax",
                self.phimax_cmap,
                self.phase_limits[0],
                self.phase_limits[1],
            ),
        )

        w3 = Wedge(
            (plot_x, plot_y),
            self.ellipse_size * pt_dict["phi_min"] / pt_dict["phi_max"],
            -1 * pt_dict["azimuth"] - self.wedge_width,
            -1 * pt_dict["azimuth"] + self.wedge_width,
            color=mtcolors.get_plot_color(
                pt_dict["phi_min"],
                "phimin",
                self.phimin_cmap,
                self.phase_limits[0],
                self.phase_limits[1],
            ),
        )
        w4 = Wedge(
            (plot_x, plot_y),
            self.ellipse_size * pt_dict["phi_min"] / pt_dict["phi_max"],
            180 - pt_dict["azimuth"] - self.wedge_width,
            180 - pt_dict["azimuth"] + self.wedge_width,
            color=mtcolors.get_plot_color(
                pt_dict["phi_min"],
                "phimin",
                self.phimin_cmap,
                self.phase_limits[0],
                self.phase_limits[1],
            ),
        )

        if pt_dict["tip_mag_re"] > 0:
            txr = (
                pt_dict["tip_mag_re"]
                * self.arrow_size
                * np.sin(np.deg2rad(pt_dict["tip_ang_re"]))
            )
            tyr = (
                pt_dict["tip_mag_re"]
                * self.arrow_size
                * np.cos(np.deg2rad(pt_dict["tip_ang_re"]))
            )

            self.ax.arrow(
                plot_x,
                plot_y,
                txr,
                tyr,
                width=self.arrow_lw,
                facecolor=self.arrow_color_real,
                edgecolor=(0, 0, 0),
                length_includes_head=False,
                head_width=self.arrow_head_width,
                head_length=self.arrow_head_length,
            )

            txi = (
                pt_dict["tip_mag_im"]
                * self.arrow_size
                * np.sin(np.deg2rad(pt_dict["tip_ang_im"]))
            )
            tyi = (
                pt_dict["tip_mag_im"]
                * self.arrow_size
                * np.cos(np.deg2rad(pt_dict["tip_ang_im"]))
            )

            self.ax.arrow(
                plot_x,
                plot_y,
                txi,
                tyi,
                width=self.arrow_lw,
                facecolor=self.arrow_color_imag,
                edgecolor=(0, 0, 0),
                length_includes_head=False,
                head_width=self.arrow_head_width,
                head_length=self.arrow_head_length,
            )

        # make an ellipse
        e1 = Ellipse(
            (plot_x, plot_y),
            width=2 * self.ellipse_size,
            height=2 * self.ellipse_size * pt_dict["phi_min"] / pt_dict["phi_max"],
            angle=90 - pt_dict["azimuth"],
        )

        gm = np.sqrt(abs(pt_dict["phi_min"]) ** 2 + abs(pt_dict["phi_max"]) ** 2)
        e1.set_facecolor(
            mtcolors.get_plot_color(
                gm,
                "geometric_mean",
                self.gm_cmap,
                self.phase_limits[0],
                self.phase_limits[1],
            )
        )
        e1.set_edgecolor(
            mtcolors.get_plot_color(
                abs(pt_dict["skew"]),
                "skew_seg",
                self.skew_cmap,
                self.skew_limits[0],
                self.skew_limits[1],
                np.arange(
                    self.skew_limits[0],
                    self.skew_limits[1] + self.skew_step,
                    self.skew_step,
                ),
            )
        )
        e1.set_linewidth(self.skew_lw)
        e1.set_alpha(self.ellipse_alpha)
        ### add patches
        for patch in [e1, w1, w2, w3, w4]:
            self.ax.add_patch(patch)

    def set_axis_labels(self, x_label, y_label):
        """
        add axis labels
        """
        self.ax.set_xlabel(x_label, fontdict={"size": self.font_size, "weight": "bold"})
        self.ax.set_ylabel(y_label, fontdict={"size": self.font_size, "weight": "bold"})

    def set_axis_limits(self, x_limits, y_limits):
        self.x_limits = x_limits
        self.y_limits = y_limits
        self.ax.set_xlim(self.x_limits)
        self.ax.set_ylim(self.y_limits)

    def get_axis_limits(self):
        """
        compute x and y limits if none given
        """
        if self.x_limits is None:
            bb = self.mt_collection.get_bounding_box()
            self.x_limits = (bb["MinLon"] - self.xpad, bb["MaxLon"] + self.xpad)
        if self.y_limits is None:
            bb = self.mt_collection.get_bounding_box()
            self.y_limits = (bb["MinLat"] - self.ypad, bb["MaxLat"] + self.ypad)

    def add_colorbar(self, location, cmap, label):
        """
        add a color bar to the axis
        """
        pass


# =============================================================================
# plot
# =============================================================================
edi_dir = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\modem_inv\inv_07\new_edis"
edi_list = glob.glob(os.path.join(edi_dir, "*.edi"))

ptm = PlotPTShapes(fn_list=edi_list)
ptm.plot()
# ec = edi_collection.EdiCollection(edilist=edi_list[:-4])
# scale = .0035
# e_cmap = 'mt_rd2wh2bl_r'
# s_cmap = 'Greys'
#
# pt_list = ec.get_phase_tensor_tippers(1.0)
#
# fig = plt.figure(1)
# fig.clf()
# ax = fig.add_subplot(1, 1, 1, aspect='equal')
# for pt_dict in pt_list:
#    ax = add_pt_patch(ax, pt_dict, scale=scale, width=5, ascale=2*scale,
#                      ecmap=e_cmap)
#
# bb = ec.get_bounding_box()
# ax.set_ylim((bb['MinLat']-scale, bb['MaxLat']+scale))
# ax.set_xlim((bb['MinLon']-scale, bb['MaxLon']+scale))
# ax.grid()
# ax.set_axisbelow(True)
#
# ax.set_xlabel('Longitude (degrees)')
# ax.set_ylabel('Latitude (degrees)')
#
#### phase color bar
# if e_cmap in list(mtcolors.cmapdict.keys()):
#    cmap_input = mtcolors.cmapdict[e_cmap]
# else:
#    cmap_input = mtcolors.cm.get_cmap(e_cmap)
# cbax = fig.add_axes([.9, .60, .015, .25])
# cb = colorbar.ColorbarBase(cbax,
#                           cmap=cmap_input,#mtcl.cmapdict[cmap],
#                           norm=colors.Normalize(vmin=0,
#                                                 vmax=90),
#                            orientation='vertical')
# cb.set_label('Phase (deg)',
#              fontdict={'size': 12, 'weight': 'bold'})
#
#### skew colorbar
# clist = [(1-cc, 1-cc, 1-cc) for cc in np.arange(0, 1 + 1. / (3), 1. / (3))]
#
## make segmented colormap
# seg_greys = colors.ListedColormap(clist)
#
## make bounds so that the middle is white
# sk_bounds = np.arange(0, 12, 3)
#
## normalize the colors
# sk_norms = colors.BoundaryNorm(sk_bounds, seg_greys.N)
#
# if s_cmap in list(mtcolors.cmapdict.keys()):
#    cmap_input = mtcolors.cmapdict[s_cmap]
# else:
#    cmap_input = mtcolors.cm.get_cmap(s_cmap)
# scbax = fig.add_axes([.9, .175, .015, .25])
# scb = colorbar.ColorbarBase(scbax,
#                            cmap=seg_greys,
#                            norm=sk_norms,
#                            orientation='vertical')
#
## label the color bar accordingly
# scb.set_label('|Skew (deg)|',
#              fontdict={'size': 12, 'weight': 'bold'})
#
# plt.show()
