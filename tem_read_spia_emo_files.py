# -*- coding: utf-8 -*-
"""

Created on Fri Jul 31 15:59:45 2020

:author: Jared Peacock

:license: MIT

"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy import interpolate

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import MultipleLocator

# =============================================================================
#
# =============================================================================
class TEMEMO:
    """
    class to hold .emo files
    
    """

    def __init__(self, fn=None):
        self._fn = None
        if fn is not None:
            self.fn = fn

        self.model = None
        self.data = None
        self.response = None
        self.model_parameters = None
        self.location = {"easting": 0, "northing": 0, "elevation": 0}
        self.doi_relative = 0
        self.doi_absolute = 0
        self.resistivity = None
        self.depth = None
        self.elevation = None

        self.channel_dict = {1: "HM-RC005", 2: "HM-RC200", 3: "LM-RC005",
                             4: "LM-RC200"}

    @property
    def fn(self):
        return self._fn

    @fn.setter
    def fn(self, fn):
        if not isinstance(fn, Path):
            fn = Path(fn)

        self._fn = fn

    def read_emo_file(self, fn=None):
        """
        read in .emo file output by SPIA
        """

        if fn is not None:
            self.fn = fn

        if not self.fn.exists():
            raise ValueError(f"File {self.fn} does not exist")

        lines = self.fn.read_text().split("\n")
        model_index = 0
        for ii, line in enumerate(lines):
            if line.startswith("Model #"):
                model_index = ii
                break
        # print(f"Model Index = {model_index}")
        # can't fucking parse the header cause its not standard, just store
        # as a list of strings.
        self.model_parameters = lines[0 : model_index - 1]

        max_iter = int(lines[model_index - 1].strip().split()[0])

        self.location = dict(
            [
                (k, float(v))
                for k, v in zip(
                    ["easting", "northing", "elevation"],
                    lines[model_index + 1].strip().split()[2:],
                )
            ]
        )

        # read model
        cols = ["iter"] + lines[model_index + 3].strip().lower().replace(
            "#", ""
        ).split()
        model_iterations = dict([(col, []) for col in cols])

        for ii in range(max_iter):
            values = lines[model_index + 4 + ii].strip().split()
            for k, v in zip(cols, values):
                model_iterations[k].append(float(v))

        model_iterations = dict(
            [(k, v) for k, v in model_iterations.items() if len(v) > 1]
        )
        m_index = [int(ii) for ii in model_iterations.pop("iter")]
        self.model = pd.DataFrame(model_iterations, index=m_index)

        # read data
        data_index = 0
        for ii, line in enumerate(
            lines[model_index + max_iter :], model_index + max_iter
        ):
            if line.startswith("Data"):
                data_index = ii
                break
        # print(f"Data Index = {data_index}")
        data_header = lines[data_index + 2].strip().replace("#", "").lower().split()
        data = dict([(key, []) for key in data_header])
        for line in lines[data_index + 3 :]:
            if "data" in line.lower():
                continue
            values = line.strip().split()
            if len(values) > 6:
                for k, v in zip(data_header, values):
                    data[k].append(float(v))

        self.data = pd.DataFrame(data)

        # get DOI
        self.doi_absolute = [float(ii) for ii in lines[-4].strip().split()]
        self.doi_relative = [float(ii) for ii in lines[-2].strip().split()]
        
        # get resistivity 
        res_keys = [col for col in self.model.columns if "res" in col]
        self.resistivity = self.model.iloc[-1][res_keys].values

        # get depth
        thick_keys = [col for col in self.model.columns if "thic" in col]
        self.depth = self.model.iloc[-1][thick_keys].values
        self.depth = [0] + \
            [self.depth[0:ii].sum() for ii in range(self.depth.size)]
        self.depth = np.array(self.depth)
        self.elevation = np.array(self.depth) - self.location["elevation"]

    def plot(self, fig_num=1, iteration=None, res_limits=[10, 5000], title=None,
             plot_elevation=True):
        """
        plot data and models
        """
        if iteration is None:
            iteration = sorted([col for col in self.data.columns if "ite" in col])[-1]
            print(f"Using iteration column: {iteration}")
        gs = gridspec.GridSpec(ncols=2, nrows=1, width_ratios=(1, 2))

        fig = plt.figure(fig_num)
        ax_t = fig.add_subplot(gs[1])
        ax_d = fig.add_subplot(gs[0])

        # plot data and response
        data_lines = []
        resp_lines = []
        data_labels = []
        resp_labels = []
        for ds in self.data.dset.unique():
            data = self.data[self.data.dset == ds]
            # plot data first
            (l1,) = ax_t.loglog(
                data.time,
                data.inp_data,
                color=(1 / ds, 0, 0),
                ls="-",
                marker="o",
                ms=2,
                lw=0.5,
            )
            data_lines.append(l1)
            data_labels.append(f"Data {self.channel_dict[int(ds)]}")

            # plot response
            (l2,) = ax_t.loglog(
                data.time,
                data[iteration],
                color=(0, 0, 1 / ds),
                ls="None",
                marker="+",
                ms=6,
            )
            resp_lines.append(l2)
            resp_labels.append(f"Resp {self.channel_dict[int(ds)]}")

        # make legend
        ax_t.legend(
            data_lines + resp_lines,
            data_labels + resp_labels,
            loc="lower left",
            ncol=1,
            fontsize=7,
        )

        # plot
        if plot_elevation:
            plot_z = self.elevation
            
        else:
            plot_z = self.depth
        ax_d.step(self.resistivity, plot_z)
        
        # check res limits
        if self.resistivity.max() > res_limits[1]:
            res_limits[1] = np.round(self.resistivity.max() ** 1.05, 2)

        if self.resistivity.min() < res_limits[0]:
            res_limits[0] = np.round(self.resistivity.min() ** 0.95, 2)

        # set axis properties
        ax_d.set_xscale("log")
        ax_d.set_xticks([1, 10, 100, 1000, 10000])
        ax_d.set_xlim(res_limits)
        ax_d.set_ylim((plot_z.max(), plot_z.min()))
        ax_d.yaxis.set_minor_locator(MultipleLocator(10))
        ax_d.yaxis.set_major_locator(MultipleLocator(50))

        # plot doi
        ax_d.fill_between(
            res_limits,
            [
                self.doi_absolute[0] - self.location["elevation"],
                self.doi_absolute[0] - self.location["elevation"],
            ],
            [
                self.doi_absolute[1] - self.location["elevation"],
                self.doi_absolute[1] - self.location["elevation"],
            ],
            color=(0.85, 0.85, 0.85),
            alpha=0.85,
        )

        ax_d.fill_between(
            res_limits,
            [
                self.doi_relative[0] - self.location["elevation"],
                self.doi_relative[0] - self.location["elevation"],
            ],
            [
                self.doi_relative[1] - self.location["elevation"],
                self.doi_relative[1] - self.location["elevation"],
            ],
            color=(0.7, 0.7, 0.7),
            alpha=0.85,
        )

        # make grid
        for ax in [ax_t, ax_d]:
            ax.grid(which="major", color=(0.5, 0.5, 0.5), lw=0.75, ls="-")
            ax.grid(which="minor", color=(0.65, 0.65, 0.65), lw=0.5, ls="--")
            ax.set_axisbelow(True)

        # set axis labels
        f_dict = {"size": 12}
        ax_t.set_xlabel("Time [s]", fontdict=f_dict)
        ax_t.set_ylabel(r"$\frac{dB}{dt}$ [$\frac{mV}{A \cdot m^4}$]", fontdict=f_dict)
        ax_d.set_xlabel(r"Resistivity [$\Omega \cdot m$]", fontdict=f_dict)
        ax_d.set_ylabel("Elevation [m]", fontdict=f_dict)

        # make tight layout to make things look nice
        fig.tight_layout()

        # plot title
        if title is not None:
            fig.suptitle(title)
            fig.subplots_adjust(top=0.92)

        fig.show()

        return fig, ax_t, ax_d
    
class EMOCollection:
    """
    collection of emo files
    """
    
    def __init__(self, fn_list):
        self._fn_list = None
        self.emo_list = None
        
        self.fn_list = fn_list
        self.profile_direction = 'ew'
        
        
    @property
    def fn_list(self):
        return self._fn_list
    
    @fn_list.setter
    def fn_list(self, fn_list):
        if not isinstance(fn_list, (list, tuple, np.ndarray)):
            raise ValueError('Input must be a list of SPIA .emo files, '+
                             f' not {type(fn_list)}')
            
        for ii, fn in enumerate(fn_list):
            if not isinstance(fn, Path):
                fn_list[ii] = Path(fn)
                if fn_list[ii].suffix.lower() not in ['.emo']:
                    raise ValueError('Input must be a SPIA .emo files, '+
                                     f' not {fn}')
                
        self._fn_list = fn_list
        
        self.emo_list = []
        for fn in self._fn_list:
            emo = TEMEMO()
            emo.read_emo_file(fn)
            self.emo_list.append(emo)
            
    def sort_profile(self, profile_direction=None):
        """
        make pandas dataframe for a profile
        """
        if profile_direction is not None:
            self.profile_direction = profile_direction
        
        direction = np.zeros(len(self.fn_list), 
                             dtype=[('index', np.int),
                                     ('easting', np.float),
                                     ('northing', np.float),
                                     ('elevation', np.float),
                                     ('name', 'U20'),
                                     ('doi_rel', np.float),
                                     ('doi_abs', np.float)])
        
        for ii in range(len(self.emo_list)):
            direction[ii]['index'] = ii
            direction[ii]['easting'] = self.emo_list[ii].location['easting'] 
            direction[ii]['northing'] = self.emo_list[ii].location['northing'] 
            direction[ii]['elevation'] = self.emo_list[ii].location['elevation']
            direction[ii]['name'] = self.fn_list[ii].name
            direction[ii]['doi_rel'] = np.mean(self.emo_list[ii].doi_relative) - \
                self.emo_list[ii].location['elevation']
            direction[ii]['doi_abs'] = np.mean(self.emo_list[ii].doi_absolute) - \
                self.emo_list[ii].location['elevation']
            
        if self.profile_direction == 'ew':
            direction = np.sort(direction, order=['easting'])
            
        elif self.profile_direction == 'ns':
            direction = np.sort(direction, order=['northing'])
            
        return direction
    
    def interpolate_model(self, dx=10, dz=50, method='linear'):
        """
        interpolate model onto grid
        
        :return: DESCRIPTION
        :rtype: TYPE

        """
        
        profile_sorted = self.sort_profile()
        
        if self.profile_direction == 'ew':
            distance = profile_sorted['easting']
        elif self.profile_direction == 'ns':
            distance = profile_sorted['northing']
        
        max_depth = max([emo.depth.max() for emo in self.emo_list])
        min_depth = min([emo.depth.min() for emo in self.emo_list])
        if min_depth == 0:
            min_depth = 1
        max_elevation = min([emo.elevation.min() for emo in self.emo_list])
        depth = np.logspace(np.log10(min_depth), np.log10(max_depth), dz)
        elevation = depth + 1 + max_elevation
        models = np.zeros((len(self.emo_list), depth.size))
        for ii, jj in enumerate(profile_sorted['index']):
            emo = self.emo_list[jj]
            f = interpolate.interp1d(emo.elevation, emo.resistivity,
                                     bounds_error=False,
                                     fill_value=np.nan)
            models[ii, :] = f(elevation)
         
        # interpolate model
        nx = int((distance.max() - distance.min()) / dx)
        new_x = np.linspace(distance.min(), distance.max(), nx)
        xb, zb = np.broadcast_arrays(distance[:, None], elevation[None, :])
        model_interp = interpolate.griddata((xb.ravel(), zb.ravel()),
                                            np.nan_to_num(models.ravel()),
                                            (new_x[:, None], elevation[None, :]),
                                            fill_value=np.nan,
                                            method=method)
        
        # interpolate doi
        print(distance)
        doi_rel_interp = interpolate.interp1d(distance,
                                              profile_sorted['doi_rel'],
                                              kind=method)
        interp_doi_rel = doi_rel_interp(new_x)
        
        return new_x, elevation, model_interp, interp_doi_rel
        
    def plot(self, dx=10, dz=40, method='linear', fig_num=1, res_limits=(0, 3)):
        """
        
        """
        
        nx, nz, model, doi = self.interpolate_model(dx=dx, dz=dz, method=method)
        
        xg, yg = np.meshgrid(nx, nz)
        
        fig = plt.figure(fig_num)
        ax = fig.add_subplot(1, 1, 1, aspect='equal')
        
        im = ax.pcolormesh(xg, yg, np.log10(model.T),
                           cmap='jet_r',
                           vmin=res_limits[0],
                           vmax=res_limits[1])
        
        l1, = ax.plot(nx, doi, ls='--', lw=1, color=(.25, .25, .25))
        ax.fill_between(nx, doi, [nz.max()]*nx.size, color=(.5, .5, .5),
                        alpha=.5)
        
        # set axis limits
        ax.set_ylim((nz.max(), nz.min()))
        
        # set labels
        ax.set_xlabel('Distance [m]')
        ax.set_ylabel('Elevation [m]')
        
        plt.colorbar(mappable=im, ax=ax, shrink=.5)
        
        return ax, fig

def get_emo_files_from_dir(emo_dir, stations=None):
    """
    get all emo files from directory
    """
    
    if not isinstance(emo_dir, Path):
        emo_dir = Path(emo_dir)
        
    emo_list = []
    for folder in emo_dir.iterdir():
        if stations is not None:
            if folder.name not in stations:
                continue
        folder_emo_list = list(folder.glob('*.emo'))
        if len(folder_emo_list) == 1:
            emo_list.append(folder_emo_list[0])
        elif len(folder_emo_list) > 1:
            emo_list += folder_emo_list
            
    return emo_list
    

# =============================================================================
# test
# =============================================================================
fn = r"c:\Users\peaco\Documents\MT\UM2020\TEM\Models\blocky\T00\_1_1.ml.emo"
t = TEMEMO(fn)
l = t.read_emo_file()
#f, ax1, ax2 = t.plot(title="TEM00")

emo_fn_list = get_emo_files_from_dir(r"c:\Users\peaco\Documents\MT\UM2020\TEM\Models\smooth",
                                     stations=['T20', 'T21', 'T22', 'T23',
                                               'T24', 'T25']) 

emo_collection = EMOCollection(emo_fn_list)
emo_collection.profile_direction = 'ns'
x, z, nm, doi = emo_collection.interpolate_model(dz=50, method='cubic')
emo_collection.plot()
