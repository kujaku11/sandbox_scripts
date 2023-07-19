# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 10:55:30 2019

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# =============================================================================
# log class
# =============================================================================
class ModEMLog(object):
    """
    class for ModEM log files
    """

    def __init__(self, log_fn=None):
        self.log_fn = log_fn
        self.log_df = pd.DataFrame()
        self._keys = ["alpha", "f", "lambda", "m2", "rms"]

    def read_log_file(self, log_fn=None):
        """
        read log file
        """
        if log_fn is not None:
            self.log_fn = log_fn

        with open(self.log_fn, "r") as fid:
            lines = fid.readlines()

        log_dict = {}
        iteration = 0
        for line in lines:
            if "start:" in line.lower() or "startls:" in line.lower():
                log_dict[iteration] = self._read_line(line)
            elif "completed" in line.lower():
                iteration = self._read_iteration_line(line)
            else:
                continue
        self.log_df = pd.DataFrame(log_dict).transpose()

    def _read_line(self, line):
        """
        read a line and return dictionary
        """
        line = line.split(":")[1].strip()
        line_dict = {}
        for ii in range(5):
            line = line.replace("= ", "=")

        for param in line.split():
            key, value = param.split("=")
            try:
                value = float(value)
            except ValueError:
                pass
            line_dict[key] = value

        return line_dict

    def _read_iteration_line(self, iteration_line):
        """
        read the iteration line
        """
        return int(iteration_line.split()[-1])

    def plot(self, subplots=False):
        """
        plot statistics
        """

        fig = plt.figure()
        if subplots:
            ax_a = fig.add_subplot(5, 1, 1)
            ax_f = fig.add_subplot(5, 1, 2, sharex=ax_a)
            ax_l = fig.add_subplot(5, 1, 3, sharex=ax_a)
            ax_m2 = fig.add_subplot(5, 1, 4, sharex=ax_a)
            ax_rms = fig.add_subplot(5, 1, 5, sharex=ax_a)

            ### plot alpha
            ax_a.plot(self.log_df.index, self.log_df.alpha)
            ax_a.xaxis.set_major_locator(MultipleLocator(5))
            ax_a.xaxis.set_minor_locator(MultipleLocator(1))
            ax_a.tick_params(labelbottom=False)
            ax_a.set_yscale("log")

            ### plot f
            ax_f.plot(self.log_df.index, self.log_df.f)
            ax_f.set_yscale("log")
            ax_f.tick_params(labelbottom=False)
            #        ax_f.set_ylim((self.log_df.f.min()*.75,
            #                       self.log_df.f.median()+self.log_df.f.std()))

            ### plot lambda
            ax_l.semilogy(self.log_df.index, self.log_df["lambda"])
            ax_l.tick_params(labelbottom=False)
            ax_l.set_yticks([10**ii for ii in range(6, -8, -1)])
            ax_l.set_ylim(
                (
                    self.log_df["lambda"].min() * 0.7,
                    self.log_df["lambda"].max() * 1.8,
                )
            )

            ### plot m2
            ax_m2.plot(self.log_df.index, self.log_df.m2)
            ax_m2.tick_params(labelbottom=False)
            ax_m2.set_ylim(
                (self.log_df.m2.min() * 0.75, self.log_df.m2.max() * 1.3)
            )

            ### plot rms
            ax_rms.plot(self.log_df.index, self.log_df.rms)
            ax_rms.set_xlabel("iteration", fontdict={"weight": "bold"})
            ax_rms.set_yscale("log")

            for ax, label in zip([ax_a, ax_f, ax_l, ax_m2, ax_rms], self._keys):
                ax.grid(which="major", lw=0.5, ls="--", color=(0.5, 0.5, 0.5))
                ax.grid(
                    which="minor", lw=0.25, ls="--", color=(0.75, 0.75, 0.75)
                )
                ax.set_ylabel(label, fontdict={"weight": "bold"})
        else:
            ax1 = fig.add_subplot(1, 1, 1)

            line_list = []
            line_labels = []
            for key in self._keys[::-1]:
                if key == "rms":
                    lw = 4
                    zorder = 10
                else:
                    lw = 2
                    zorder = 3
                try:
                    (l1,) = ax1.plot(
                        self.log_df.index,
                        self.log_df[key],
                        lw=lw,
                        zorder=zorder,
                    )
                except ValueError:
                    print(key)
                    continue
                line_list.append(l1)
                line_labels.append(key.capitalize())

            ax1.set_yscale("log")
            ax1.set_xlabel("iteration", fontdict={"size": 12, "weight": "bold"})
            ax1.xaxis.set_major_locator(MultipleLocator(10))
            ax1.xaxis.set_minor_locator(MultipleLocator(1))

            ax1.grid(which="major", ls="--", color=(0.5, 0.5, 0.5), zorder=0)
            ax1.grid(which="minor", ls="--", color=(0.75, 0.75, 0.75), zorder=0)
            ax1.legend(line_list, line_labels, prop={"size": 12})

        plt.show()


# =============================================================================
# Tests
# =============================================================================
# =============================================================================
# Inputs
# =============================================================================
log_fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\modem_inv\inv_large_grid\gz_2017_z03_c021_NLCG.log"

log_obj = ModEMLog(log_fn)
log_obj.read_log_file()
log_obj.plot()

# log_line = "START: f=5.182165E+02 m2=5.127418E+00 rms=   2.339822 lambda=1.000000E+02 alpha=2.000000E+01"
# p = log_obj._read_line(log_line)
# print(p)
