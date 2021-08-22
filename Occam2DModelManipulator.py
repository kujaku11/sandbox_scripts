# -*- coding: utf-8 -*-
"""
Created on Thu Nov 08 15:18:54 2012

@author: jpea562
"""

# import mtpy.modeling.occamtools as occam
import mtpy.modeling.occam2d as occam2d
import matplotlib.pyplot as plt
import numpy as np
import string
import matplotlib.widgets as widgets
import os


class Occam2DModelManipulator(occam2d.Occam2DModel):
    """
    will plot the occam model and let the user change the resistivity values.
    
    """

    def __init__(self, iterfn):
        self.iterfn = iterfn

        # make a default resistivity range on a log scale
        self.res_num = 9
        self.res_min = 0
        self.res_max = 4
        self.res_range = None
        self.res_dict = None
        self.res_ii = None
        self.res_value = None
        self.res_fix = False

        # --> alphabet list for mesh file, corresponding to resistivity values
        self._alpha_lst = " ".join(string.ascii_lowercase).split()
        self.alpha_dict = None

        # create a default resistivity list
        self._make_resisitivity_range(self.res_min, self.res_max, self.res_num)

        # plotting attributes and connections
        self.mesh_plot = None
        self.cid = None
        self.cid_pmres = None

        self.radio_res_loc = [0.10, 0.1, 0.1, 0.25]
        self.radio_res_ax = None
        self.radio_res_labels = None
        self.radio_res = None

        self.eventR = None
        self.eventPM = None

        self.mesh_width = 200.0

        self.new_model_fn = None

    def plotResModel(self, res_range=(0, 4), res_num=9):
        """
        plot the resistivity model with finite element mesh on and scale is
        in meters, which makes everything a lot easier to handle at the 
        moment.
        
        """
        self._make_resisitivity_range(res_range[0], res_range[1], res_num)

        # call plot2DmModel to draw figure and plot mesh grid
        self.mesh_plot = self.plot2DModel(femesh="on", yscale="m")

        # connect to a button press event for changing resistivity values in
        # the plot
        self.cid = self.mesh_plot.ax.figure.canvas.mpl_connect(
            "button_press_event", self.get_mclick_xy
        )

        # connect to a key press event for changing resistivity values
        self.cid_pmres = self.mesh_plot.ax.figure.canvas.mpl_connect(
            "key_press_event", self.pmRes
        )

        # make a rectangular selector
        self.rect_selector = widgets.RectangleSelector(
            self.mesh_plot.ax, self.rect_onselect, drawtype="box", useblit=True
        )

        # make a radio boxe for changing the resistivity values easily
        self.radio_res_ax = self.mesh_plot.fig.add_axes(self.radio_res_loc)
        self.radio_res_labels = ["air", "sea"] + [
            "{0:.4g}".format(rr) for rr in self.res_range[2:]
        ]

        self.radio_res = widgets.RadioButtons(
            self.radio_res_ax, self.radio_res_labels, active=self.res_ii
        )
        self.radio_res.on_clicked(self.set_res_value)

        # calculate minimum block width
        self.mesh_width = np.min(
            [
                abs(om.meshx[0, ii + 1] - xx)
                for ii, xx in enumerate(self.meshx[0, 7:-7], 7)
            ]
        )

        self._caluculate_midpoints()

    def create_triangular_mesh(self):
        """
        create a triangular mesh to manipulate
        """
        verts = []
        for xi, xx in enumerate(self.plotx[:-1]):
            for yi, yy in enumerate(self.ploty[:-1]):
                v1 = (xx, yy)
                v2 = (xx, om.ploty[yi + 1])
                v3 = (om.plotx[xi + 1], om.ploty[yi + 1])
                v4 = (om.plotx[xi + 1], yy)
                v5 = (
                    xx + (om.plotx[xi + 1] - xx) / 2,
                    yy + (om.ploty[yi + 1] - yy) / 2,
                )
                verts.append((v1, v5, v4))
                verts.append((v1, v5, v2))
                verts.append((v2, v5, v3))
                verts.append((v3, v5, v4))

    def _caluculate_midpoints(self):
        """
        calculate mid points of the mesh squares to locate the cursor and 
        decide which triangles to color.
        
        """

        # calculate mid points in x direction
        self.xmid = np.array(
            [
                self.plotx[ii] + (self.plotx[ii + 1] - self.plotx[ii]) / 2
                for ii in range(len(self.plotx[:-1]))
            ]
        )

        self.ymid = np.array(
            [
                self.ploty[ii] + (self.ploty[ii + 1] - self.ploty[ii]) / 2
                for ii in range(len(self.ploty[:-1]))
            ]
        )

        # calculate tolerance for each cell to pick around
        self.xpick_tol = np.array(
            [
                0.9 * (self.plotx[ii + 1] - self.plotx[ii]) / 2
                for ii in range(len(self.plotx[:-1]))
            ]
        )
        self.ypick_tol = np.array(
            [
                0.9 * (self.ploty[ii + 1] - self.ploty[ii]) / 2
                for ii in range(len(self.ploty[:-1]))
            ]
        )

    def _make_resisitivity_range(self, res_min, res_max, res_num):
        """
        create a range of resistivities on a log scale for res_num of 
        resistivities
        
        Arguments:
        -----------
            **res_min** : minimum resistivity value on log10 scale
            
            **res_max** : maximum resistivity value on log10 scale
            
            **res_num** : number of resistivity values between 
                          res_min and res_max
        
        """
        self.res_min = res_min
        self.res_max = res_max
        self.res_num = res_num

        # make a default resistivity range on a log scale
        self.res_range = np.array([13, np.log10(0.3)])
        self.res_range = np.append(
            self.res_range,
            np.array(
                [ii for ii in np.linspace(self.res_min, self.res_max, num=self.res_num)]
            ),
        )

        self.res_dict = dict(
            [(rkey, rvalue) for rvalue, rkey in enumerate(self.res_range)]
        )

        # start the resistivity index in the middle of the range
        self.res_ii = int(self.res_num / 2)

        # set resistivity value
        self.res_value = self.res_range[self.res_ii]

        # --> alphabet list for mesh file, corresponding to resistivity values
        self.alpha_dict = dict(
            [
                (rr, aa.upper())
                for rr, aa in zip(self.res_range[2:], self._alpha_lst[0 : self.res_num])
            ]
        )
        self.alpha_dict[13] = "0"
        self.alpha_dict[np.log10(0.3)] = "Z"

    def get_mclick_xy(self, event):
        """
        change the resistivity values for selected cell
        """

        self.eventR = event
        if self.eventR.button == 3:

            xx = self.eventR.xdata
            yy = self.eventR.ydata

            x_change = np.where(
                (self.plotx > xx - self.mesh_width)
                & (self.plotx < xx + self.mesh_width)
            )[0][0]

            y_change = np.where((self.ploty > yy * 0.95) & (self.ploty < yy * 1.05))[0][
                0
            ]

            self.change_model_res(int(x_change), int(y_change))

    def change_model_res(self, xchange, ychange):
        """                    
        change the resistivity values in the model file and mesh file
        
        and replot the data to change the figure
        """

        # change the resistivity value in the model
        # shape of resmodel is y, x
        if type(xchange) is int and type(ychange) is int:
            self.resmodel[ychange, xchange] = self.res_value
            self.meshdata[xchange, -ychange, :] = [self.alpha_dict[self.res_value]] * 4
        else:
            for xx in xchange:
                for yy in ychange:
                    self.resmodel[yy, xx] = self.res_value
                    self.meshdata[xx, self.ploty.shape[0] - yy - 1, :] = [
                        self.alpha_dict[self.res_value]
                    ] * 4

        self.mesh_plot.ax.pcolormesh(
            self.meshx,
            self.meshy,
            self.resmodel,
            cmap=self.mesh_plot.cmap,
            vmin=self.res_min,
            vmax=self.res_max,
        )
        self._update_plot()

        # for the meshdata the y-indices needs to be negative cause counts from
        # top down --> check on this

    #        self.meshdata[xchange, self.ploty.shape[0]-ychange-1, :] = \
    #                                           [self.alpha_dict[self.res_value]]*4

    def _update_plot(self):
        """
        redraw the figure
        """

        self.mesh_plot.ax.figure.canvas.draw()

    def pmRes(self, event):
        self.eventPM = event
        if self.eventPM.key == "=":
            self.res_ii += 1
            print "Increased Resistivity to {0:.1f} Ohm-m".format(
                self.resrange[self.res_ii]
            )
        elif self.eventPM.key == "-":
            self.res_ii -= 1
            print "Decreased Resistivity to {0:.1f} Ohm-m".format(
                self.resrange[self.res_ii]
            )

        elif self.eventPM.key == "q":
            self.eventPM.canvas.mpl_disconnect(self.cid)
            self.eventPM.canvas.mpl_disconnect(self.cid_pmres)
            plt.close(self.eventPM.canvas.figure)
            if self.res_fix == True:
                self.rewriteMeshFile()

            self.rewrite_iter_fn()

    def set_res_value(self, label):
        """
        set the resistivity value of the radio box and internally
        
        """

        self.res_ii = np.where(np.array(self.radio_res_labels) == label)[0][0]
        self.res_value = self.res_range[self.res_ii]

    def rect_onselect(self, eclick, erelease):
        """
        on selecting a rectangle change the colors to the resistivity values
        """

        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        x_change = self._get_x_index(x1, x2)
        y_change = self._get_y_index(y1, y2)

        # reset values of resistivity
        self.change_model_res(x_change, y_change)

    def _get_x_index(self, x1, x2):
        """
        get the index value of the points to be changed
        
        """
        if x1 < x2:
            xchange = np.where((self.plotx >= x1) & (self.plotx <= x2))[0]
            if len(xchange) == 0:
                print x1, x2, x1 + (x2 - x1) / 2, xchange, self.mesh_width
                xchange = np.where(
                    (self.plotx > x1 + (x2 - x1) / 2 - self.mesh_width)
                    & (self.plotx < x1 + (x2 - x1) / 2 + self.mesh_width)
                )[0][0]

                return [xchange]

        if x1 > x2:
            xchange = np.where((self.plotx <= x1) & (self.plotx >= x2))[0]
            if len(xchange) == 0:
                xchange = np.where(
                    (self.plotx > x2 + (x1 - x2) / 2 - self.mesh_width)
                    & (self.plotx < x2 + (x1 - x2) / 2 + self.mesh_width)
                )[0][0]
                print xchange
                return [xchange]

        # check the edges to see if the selection should include the square
        xchange = np.append(xchange, xchange[0] - 1)
        xchange.sort()

        return xchange

    def _get_y_index(self, y1, y2):
        """
        get the index value of the points to be changed in north direction
        
        need to flip the index because the plot is flipped
        
        """

        if y1 < y2:
            ychange = np.where((self.ploty > y1) & (self.ploty < y2))[0]
            if len(ychange) == 0:
                ychange = np.where(
                    (self.ploty > (y2 + y1) / 2 * 0.95)
                    & (self.ploty < (y2 + y1) / 2 * 1.05)
                )[0][0]
                print ychange
                return [ychange]

        elif y1 > y2:
            ychange = np.where((self.ploty < y1) & (self.ploty > y2))[0]
            if len(ychange) == 0:
                ychange = np.where(
                    (self.ploty > (y1 + y2) / 2 * 0.95)
                    & (self.ploty < (y1 + y2) / 2 * 1.05)
                )[0][0]
                print ychange
                return [ychange]

        ychange -= 1
        ychange = np.append(ychange, ychange[-1] + 1)

        return ychange

    def rewriteMeshFile(self):
        """
        rewrite mesh file so the changed values are correct
        
        """
        # check the mesh
        mfid = open(self.meshfn, "r")
        mlines = mfid.readlines()
        mfid.close()

        mfid = open(self.meshfn + "_RW", "w")
        mfid.write(mlines[0])

        # write the second line replacing the number of fixed resistivities
        mline = mlines[1].strip().split()
        mline[3] = str(self.res_num)
        mfid.write(" " + "".join(["{:>6}".format(ss) for ss in mline]) + "\n")

        # write list of resistivities in linear scale
        mfid.write(
            "\n".join(["     {:.5g}".format(10 ** rr) for rr in om.res_range[2:]])
        )
        mfid.write("\n")

        mline = 1
        ii = 2
        while mline != ["0"]:
            mline = mlines[ii].strip().split()
            mfid.write(mlines[ii])
            ii += 1

        for ii in range(self.meshdata.shape[1]):
            for mm in range(4):
                for jj in range(self.meshdata.shape[0]):

                    mfid.write(self.meshdata[jj, ii, mm])
                mfid.write("\n")
        mfid.close()

        print "Rewrote mesh to {0}".format(self.meshfn + "_RW")

    def rewrite_iter_fn(self):
        """
        rewrite the startup file as a starting model
        
        """
        sfid = open(self.iterfn, "r")
        slines = sfid.readlines()
        sfid.close()

        self.new_model_fn = os.path.join(os.path.dirname(self.iterfn), "StartingModel")
        sfid = open(self.new_model_fn, "w")
        sline = " "
        ii = 0
        while sline.lower().find("para") == -1:
            sline = slines[ii].lower()
            sfid.write(slines[ii])
            ii += 1

        write_res = np.flipud(self.resmodel)
        reslst = []
        ii = 0
        for ii in range(len(self.rows)):
            # get the number of layers to combine
            # this index will be the first index in the vertical direction
            ny1 = self.rows[:ii, 0].sum()
            # the second index  in the vertical direction
            ny2 = ny1 + self.rows[ii][0]
            # make the list of amalgamated columns an array for ease
            lc = np.array(self.cols[ii])
            # loop over the number of amalgamated blocks
            for jj in range(len(self.cols[ii])):
                # get first in index in the horizontal direction
                nx1 = lc[:jj].sum()
                # get second index in horizontal direction
                nx2 = nx1 + lc[jj]
                # put the apporpriate resistivity value into all the amalgamated
                # model blocks of the regularization grid into the forward model
                # grid
                res = "{: .6f}".format(np.median(write_res[ny1:ny2, nx1:nx2]))
                reslst.append("{:>15}".format(res))

        for rr, res in enumerate(reslst):
            sfid.write(res)
            if np.remainder(rr, 4) == 0 and rr != 0:
                sfid.write("\n")

        sfid.close()

        print "Saved new starting model to {0}".format(self.new_model_fn)


itfn = r"c:\MinGW32-xy\Peacock\occam\MonoBasin\MT\Line1\Inv2_TM_SMPhase_SM2\Line1_TM_SMPhase_SM2_07.iter"
om = Occam2DModelManipulator(itfn)
om.plotResModel()
