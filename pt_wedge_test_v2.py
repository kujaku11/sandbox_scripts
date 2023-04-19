# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 12:06:03 2019

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np
from matplotlib.ticker import FormatStrFormatter
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colorbar as mcb
import matplotlib.colors as colors

try:
    import contextily as cx

    has_cx = True
except ModuleNotFoundError:
    has_cx = False

from mtpy.imaging.mtplot_tools import PlotBaseMaps, add_raster
from mtpy.core import Z, Tipper
from mtpy.imaging import mtcolors
from mtpy.core.transfer_function import PhaseTensor


# ==============================================================================


class PlotPTShapes(PlotBaseMaps):
    """
    plot phase tensor ellipses and lines
    """

    def __init__(self, mt_data, **kwargs):
        super().__init__(**kwargs)

        self._rotation_angle = 0
        self.mt_data = mt_data

        self.plot_station = False
        self.plot_period = 1.0

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
        # read in map scale
        self.map_scale = "deg"
        self.map_utm_zone = None
        self.map_epsg = None

        self.minorticks_on = True
        self.x_pad = 0.01
        self.y_pad = 0.01

        # set a central reference point
        self.reference_point = (0, 0)

        self.cx_source = None
        self.cx_zoom = None
        if has_cx:
            self.cx_source = cx.providers.USGS.USTopo

        # station labels
        self.station_id = (0, 2)
        self.station_pad = 0.0005

        self.arrow_legend_fontdict = {"size": self.font_size, "weight": "bold"}
        self.station_font_dict = {"size": self.font_size, "weight": "bold"}

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.fig = None

    @property
    def map_scale(self):
        return self._map_scale

    @map_scale.setter
    def map_scale(self, map_scale):
        self._map_scale = map_scale

        if self._map_scale in ["deg", "latlon", "ll"]:
            self.xpad = 0.005
            self.ypad = 0.005
            self.ellipse_size = 0.005
            self.arrow_size = 0.005
            self.arrow_head_length = 0.0025
            self.arrow_head_width = 0.0035
            self.arrow_lw = 0.00075

            self.tickstrfmt = "%.3f"
            self.y_label = "Latitude (deg)"
            self.x_label = "Longitude (deg)"

        elif self._map_scale == "m":
            self.xpad = 1000
            self.ypad = 1000
            self.ellipse_size = 500
            self.arrow_size = 500
            self.arrow_head_length = 250
            self.arrow_head_width = 350
            self.arrow_lw = 50
            self.tickstrfmt = "%.0f"
            self.x_label = "Easting (m)"
            self.y_label = "Northing (m)"

        elif self._map_scale == "km":
            self.xpad = 1
            self.ypad = 1
            self.ellipse_size = 0.500
            self.arrow_size = 0.5
            self.arrow_head_length = 0.25
            self.arrow_head_width = 0.35
            self.arrow_lw = 0.075
            self.tickstrfmt = "%.0f"
            self.x_label = "Easting (km)"
            self.y_label = "Northing (km)"

        else:
            raise ValueError(f"map scale {map_scale} is not supported.")

    # ---need to rotate data on setting rotz
    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        """
        only a single value is allowed
        """
        for tf in self.mt_data:
            tf.rotation_angle = value
        self._rotation_angle = value

    def _get_pt(self, tf):
        """
        Get phase tensor object from TF object

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """
        z = self._get_interpolated_z(tf)
        z_error = self._get_interpolated_z_error(tf)

        pt_obj = PhaseTensor(z=z, z_error=z_error)

        new_t_obj = None
        if tf.has_tipper():

            t = self._get_interpolated_t(tf)
            t_err = self._get_interpolated_t_err(tf)

            if (t != 0).all():
                new_t_obj = Tipper(t, t_err, [1.0 / self.plot_period])

        return pt_obj, new_t_obj

    def add_pt_patch(self, tf):
        """
        Add patches to plot
        """

        pt_obj, t_obj = self._get_pt(tf)

        # if map scale is lat lon set parameters
        if self.map_scale == "deg":
            plot_x = tf.longitude - self.reference_point[0]
            plot_y = tf.latitude - self.reference_point[1]
        # if map scale is in meters easting and northing
        elif self.map_scale in ["m", "km"]:
            tf.project_point_ll2utm(
                epsg=self.map_epsg, utm_zone=self.map_utm_zone
            )

            plot_x = tf.east - self.reference_point[0]
            plot_y = tf.north - self.reference_point[1]
            if self.map_scale in ["km"]:
                plot_x /= 1000.0
                plot_y /= 1000.0
        else:
            raise NameError("mapscale not recognized")
        # --> set local variables
        phimin = np.nan_to_num(pt_obj.phimin)[0]
        phimax = np.nan_to_num(pt_obj.phimax)[0]
        eangle = np.nan_to_num(pt_obj.azimuth)[0]

        # color_array = self.get_pt_color_array(pt_obj)
        # bounds = np.arange(
        #     self.ellipse_range[0],
        #     self.ellipse_range[1] + self.ellipse_range[2],
        #     self.ellipse_range[2],
        # )

        has_ellipse = True
        w1 = patches.Wedge(
            (plot_x, plot_y),
            self.ellipse_size,
            90 - eangle - self.wedge_width,
            90 - eangle + self.wedge_width,
            color=mtcolors.get_plot_color(
                phimax,
                "phimax",
                self.phimax_cmap,
                self.phase_limits[0],
                self.phase_limits[1],
            ),
        )
        w2 = patches.Wedge(
            (plot_x, plot_y),
            self.ellipse_size,
            270 - eangle - self.wedge_width,
            270 - eangle + self.wedge_width,
            color=mtcolors.get_plot_color(
                phimax,
                "phimax",
                self.phimax_cmap,
                self.phase_limits[0],
                self.phase_limits[1],
            ),
        )

        w3 = patches.Wedge(
            (plot_x, plot_y),
            self.ellipse_size * phimin / phimax,
            -1 * eangle - self.wedge_width,
            -1 * eangle + self.wedge_width,
            color=mtcolors.get_plot_color(
                phimin,
                "phimin",
                self.phimin_cmap,
                self.phase_limits[0],
                self.phase_limits[1],
            ),
        )
        w4 = patches.Wedge(
            (plot_x, plot_y),
            self.ellipse_size * phimin / phimax,
            180 - eangle - self.wedge_width,
            180 - eangle + self.wedge_width,
            color=mtcolors.get_plot_color(
                phimin,
                "phimin",
                self.phimin_cmap,
                self.phase_limits[0],
                self.phase_limits[1],
            ),
        )

        has_tipper = False
        if t_obj is not None:
            if "r" in self.plot_tipper == "yri":
                if t_obj.mag_real[0] <= self.arrow_threshold:
                    has_tipper = True
                    txr = (
                        t_obj.mag_real[0]
                        * self.arrow_size
                        * np.sin(
                            np.deg2rad(t_obj.angle_real[0])
                            + self.arrow_direction * np.pi
                        )
                    )
                    tyr = (
                        t_obj.mag_real[0]
                        * self.arrow_size
                        * np.cos(
                            np.deg2rad(t_obj.angle_real[0])
                            + self.arrow_direction * np.pi
                        )
                    )

                    self.ax.arrow(
                        plot_x,
                        plot_y,
                        txr,
                        tyr,
                        width=self.arrow_lw,
                        facecolor=self.arrow_color_real,
                        edgecolor=self.arrow_color_real,
                        length_includes_head=False,
                        head_width=self.arrow_head_width,
                        head_length=self.arrow_head_length,
                    )
                else:
                    pass

            # plot imaginary tipper
            if "i" in self.plot_tipper:
                if t_obj.mag_imag[0] <= self.arrow_threshold:
                    has_tipper = True
                    txi = (
                        t_obj.mag_imag[0]
                        * self.arrow_size
                        * np.sin(
                            np.deg2rad(t_obj.angle_imag[0])
                            + self.arrow_direction * np.pi
                        )
                    )
                    tyi = (
                        t_obj.mag_imag[0]
                        * self.arrow_size
                        * np.cos(
                            np.deg2rad(t_obj.angle_imag[0])
                            + self.arrow_direction * np.pi
                        )
                    )

                    self.ax.arrow(
                        plot_x,
                        plot_y,
                        txi,
                        tyi,
                        width=self.arrow_lw,
                        facecolor=self.arrow_color_imag,
                        edgecolor=self.arrow_color_imag,
                        length_includes_head=False,
                        head_width=self.arrow_head_width,
                        head_length=self.arrow_head_length,
                    )

        # make an ellipse
        e1 = patches.Ellipse(
            (plot_x, plot_y),
            width=2 * self.ellipse_size,
            height=2 * self.ellipse_size * phimin / phimax,
            angle=90 - eangle,
        )

        # geometric mean of phimin and phimax
        gm = np.sqrt(abs(phimin) * abs(phimax))
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
                abs(pt_obj.skew),
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

        if has_ellipse or has_tipper:
            return plot_x, plot_y
        else:
            return (0, 0)

    def _get_tick_format(self):
        """

        :return: DESCRIPTION
        :rtype: TYPE

        """

        # set tick parameters depending on the mapscale
        if self.map_scale == "deg":
            self.tickstrfmt = "%.2f"
        elif self.map_scale == "m" or self.map_scale == "km":
            self.tickstrfmt = "%.0f"

    def _set_axis_labels(self):
        # --> set axes properties depending on map scale------------------------
        if self.map_scale == "deg":
            self.ax.set_xlabel(
                "Longitude", fontsize=self.font_size, fontweight="bold"  # +2,
            )
            self.ax.set_ylabel(
                "Latitude", fontsize=self.font_size, fontweight="bold"  # +2,
            )
        elif self.map_scale == "m":
            self.ax.set_xlabel(
                "Easting (m)",
                fontsize=self.font_size,
                fontweight="bold",  # +2,
            )
            self.ax.set_ylabel(
                "Northing (m)",
                fontsize=self.font_size,
                fontweight="bold",  # +2,
            )
        elif self.map_scale == "km":
            self.ax.set_xlabel(
                "Easting (km)",
                fontsize=self.font_size,
                fontweight="bold",  # +2,
            )
            self.ax.set_ylabel(
                "Northing (km)",
                fontsize=self.font_size,
                fontweight="bold",  # +2,
            )

    def _add_colorbar(self):
        """
        Add phase tensor color bar

        :return: DESCRIPTION
        :rtype: TYPE

        """

        if self.cb_position is None:
            self.ax2, kw = mcb.make_axes(
                self.ax, orientation=self.cb_orientation, shrink=0.35
            )

        else:
            self.ax2 = self.fig.add_axes(self.cb_position)

        # make the colorbar
        if self.ellipse_cmap in list(mtcolors.cmapdict.keys()):
            cmap_input = mtcolors.cmapdict[self.ellipse_cmap]
        else:
            cmap_input = mtcolors.cm.get_cmap(self.ellipse_cmap)

        if "seg" in self.ellipse_cmap:
            norms = colors.BoundaryNorm(self.ellipse_cmap_bounds, cmap_input.N)
            self.cb = mcb.ColorbarBase(
                self.ax2,
                cmap=cmap_input,
                norm=norms,
                orientation=self.cb_orientation,
                ticks=self.ellipse_cmap_bounds,
            )
        else:
            self.cb = mcb.ColorbarBase(
                self.ax2,
                cmap=cmap_input,
                norm=colors.Normalize(
                    vmin=self.ellipse_range[0], vmax=self.ellipse_range[1]
                ),
                orientation=self.cb_orientation,
            )

        # label the color bar accordingly
        self.cb.set_label(
            self.cb_label_dict[self.ellipse_colorby],
            fontdict={"size": self.font_size, "weight": "bold"},
        )

        # place the label in the correct location
        if self.cb_orientation == "horizontal":
            self.cb.ax.xaxis.set_label_position("top")
            self.cb.ax.xaxis.set_label_coords(0.5, 1.3)
        elif self.cb_orientation == "vertical":
            self.cb.ax.yaxis.set_label_position("right")
            self.cb.ax.yaxis.set_label_coords(1.25, 0.5)
            self.cb.ax.yaxis.tick_left()
            self.cb.ax.tick_params(axis="y", direction="in")

    def plot(
        self,
        fig=None,
        save_path=None,
        show=True,
        raster_file=None,
        raster_kwargs={},
    ):
        """
        plot pts
        """
        if self.fig is None:
            self.fig = plt.figure(self.fig_num, self.fig_size)
        self.fig.clf()

        self.ax = self.fig.add_subplot(1, 1, 1, aspect="equal")

        self.plot_xarr = np.zeros(len(self.mt_data))
        self.plot_yarr = np.zeros(len(self.mt_data))
        for index, tf in enumerate(self.mt_data.values()):
            plot_x, plot_y = self.add_pt_patch(tf)
            self.plot_xarr[index] = plot_x
            self.plot_yarr[index] = plot_y

            # ------------Plot station name------------------------------
            if self.plot_station:
                self.ax.text(
                    plot_x,
                    plot_y + self.station_pad,
                    tf.station[self.station_id[0] : self.station_id[1]],
                    horizontalalignment="center",
                    verticalalignment="baseline",
                    fontdict=self.station_font_dict,
                )

        self._set_axis_labels()
        # --> set plot limits
        #    need to exclude zero values from the calculation of min/max!!!!
        self.ax.set_xlim(
            self.plot_xarr[np.nonzero(self.plot_xarr)].min() - self.x_pad,
            self.plot_xarr[np.nonzero(self.plot_xarr)].max() + self.x_pad,
        )
        self.ax.set_ylim(
            self.plot_yarr[np.nonzero(self.plot_yarr)].min() - self.y_pad,
            self.plot_yarr[np.nonzero(self.plot_xarr)].max() + self.y_pad,
        )

        # --> set tick label format
        self.ax.xaxis.set_major_formatter(FormatStrFormatter(self.tickstrfmt))
        self.ax.yaxis.set_major_formatter(FormatStrFormatter(self.tickstrfmt))
        plt.setp(self.ax.get_xticklabels(), rotation=45)

        ## rasterio for plotting geotiffs or other geophysical data.
        if raster_file is not None:
            self.raster_ax, self.raster_cb = add_raster(
                self.ax, raster_file, **raster_kwargs
            )

        else:
            if has_cx:
                try:
                    cx_kwargs = {"source": self.cx_source, "crs": "EPSG:4326"}
                    if self.cx_zoom is not None:
                        cx_kwargs["zoom"] = self.cx_zoom
                    cx.add_basemap(
                        self.ax,
                        **cx_kwargs,
                    )
                except Exception as error:
                    self.logger.warning(
                        f"Could not add base map because {error}"
                    )

        # --> set title in period or frequency
        titlefreq = "{0:.5g} (s)".format(self.plot_period)

        if not self.plot_title:
            self.ax.set_title(
                "Phase Tensor Map for " + titlefreq,
                fontsize=self.font_size + 2,
                fontweight="bold",
            )
        else:
            self.ax.set_title(
                self.plot_title + titlefreq,
                fontsize=self.font_size + 2,
                fontweight="bold",
            )

        # make a grid with color lines
        self.ax.grid(
            True, alpha=0.3, which="major", color=(0.5, 0.5, 0.5), lw=0.75
        )
        self.ax.grid(
            True,
            alpha=0.3,
            which="minor",
            color=(0.5, 0.5, 0.5),
            lw=0.5,
            ls=":",
        )
        if self.minorticks_on:
            plt.minorticks_on()  # turn on minor ticks automatically

        self.ax.set_axisbelow(True)

        self._add_colorbar()

        self.fig.show()


# # =============================================================================
# # plot
# # =============================================================================
from pathlib import Path
from mtpy import MT
from mtpy.core.mt_data import MTData

edi_dir = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\modem_inv\inv_07\new_edis"
)

md = MTData()
for edi_fn in edi_dir.glob("*.edi"):
    m = MT(edi_fn)
    m.read_tf_file()
    md.add_station(m)


# ptm = PlotPTShapes(md)
# ptm.plot()
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
#                           cmap=cmap_input,#mtcolors.cmapdict[cmap],
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
