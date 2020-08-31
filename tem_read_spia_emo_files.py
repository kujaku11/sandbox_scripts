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

from mtpy.imaging import mtcolors

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
        self.norms = None
        self.model_date = None

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
        norm_index = 0
        for ii, line in enumerate(lines):
            if line.startswith("Norm's"):
                norm_index = ii
            if line.startswith("Model #"):
                model_index = ii
                break
        # print(f"Model Index = {model_index}")
        # can't fucking parse the header cause its not standard, just store
        # as a list of strings.
        self.model_parameters = lines[0 : model_index - 1]
        date_list = self.model_parameters[5].strip().split()
        date = '-'.join(date_list[1].split('.')[::-1])
        self.model_date = f"{date}T{date_list[0]}"
        
        # get norms/rms
        norm_keys = lines[norm_index + 1].strip().replace('_#', '').lower().split()
        norm_dict = dict([(k, []) for k in norm_keys])
        for ii in range(norm_index + 2, model_index, 1):
            values = [float(vv) for vv in lines[ii].strip().split()]
            for k, v in zip(norm_keys, values):
                norm_dict[k].append(v)
        n_index = np.array(norm_dict.pop('ite'), dtype=np.int)
        self.norms = pd.DataFrame(norm_dict, index=n_index)
        max_iter = self.norms.index.max()

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
        self.doi_absolute = np.array([float(ii) for ii in lines[-4].strip().split()])
        self.doi_relative = np.array([float(ii) for ii in lines[-2].strip().split()])
        
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
        fig.clf()
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
                color=(1 / ds, 0, .2),
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
                color=(0, ds / 4, 1 / ds),
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
            hatch='X'
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
            hatch='X'
        )

        # make grid
        for ax in [ax_t, ax_d]:
            ax.grid(which="major", color=(0.65, 0.65, 0.65), lw=0.5, ls="-")
            ax.grid(which="minor", color=(0.75, 0.75, 0.75), lw=0.25, ls="--")
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
            fig.suptitle(f"{title}; RMS = {self.norms.iloc[-1].total}",
                         fontdict=f_dict)
            fig.subplots_adjust(top=0.92)

        #fig.show()

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
        nmodels = np.zeros((len(self.emo_list) + 2, depth.size)) 
        nmodels[0] = models[0]
        nmodels[1:-1] = models[:]
        nmodels[-1] = models [-1] 
        models = nmodels
        # add a block on each side for easier plotting
        
        distance = np.append(np.append(distance[0] - 100, distance),
                             distance[-1] + 100)
        
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
        doi_rel = np.append(np.append(profile_sorted['doi_rel'][0], 
                                      profile_sorted['doi_rel']),
                            profile_sorted['doi_rel'][-1])
        doi_rel_interp = interpolate.interp1d(distance,
                                              doi_rel,
                                              kind=method)
        interp_doi_rel = doi_rel_interp(new_x)
        
        return new_x, elevation, model_interp, interp_doi_rel
        
    def plot(self, dx=10, dz=40, method='linear', fig_num=1, res_limits=(0, 3),
             ypad=20, xpad=10, cmap='jet_r'):
        """
        
        """
        
        nx, nz, model, doi = self.interpolate_model(dx=dx, dz=dz, method=method)
        nmean = nx.mean()
        nx -= nmean
        xg, yg = np.meshgrid(nx, nz)
        
        fig = plt.figure(fig_num)
        fig.clf()
        ax = fig.add_subplot(1, 1, 1, aspect='equal')
        
        im = ax.pcolormesh(xg, yg, np.log10(model.T),
                           cmap=cmap,
                           vmin=res_limits[0],
                           vmax=res_limits[1])
        
        l1, = ax.plot(nx, doi, ls='--', lw=1, color=(.25, .25, .25))
        ax.fill_between(nx, doi, [nz.max()]*nx.size, color=(.5, .5, .5),
                        alpha=.5, hatch='X')
        
        # set axis limits
        ax.set_ylim((nz.max(), nz.min() - ypad))
        ax.set_xlim((nx.min() - xpad, nx.max() + xpad))
        
        # set labels
        if self.profile_direction == 'ew':
            ax.set_xlabel('Easting [m]')
        elif self.profile_direction == 'ns':
            ax.set_xlabel('Northing [m]')
        ax.set_ylabel('Elevation [m]')
        ax.xaxis.set_minor_locator(MultipleLocator(10))
        ax.yaxis.set_minor_locator(MultipleLocator(10))
        
        cx = plt.colorbar(mappable=im, ax=ax, shrink=.75)
        cx.set_label('Resistivity [$\Omega \cdot m$]')
        cx.set_ticks([0, 1, 2, 3, 4])
        cx.set_ticklabels(['$10^{0}$', '$10^{1}$', '$10^{2}$', '$10^{3}$', '$10^{4}$'])
        
        # plot stations
        for emo in self.emo_list:
            if self.profile_direction == 'ew':
                sx = emo.location['easting'] - nmean
            elif self.profile_direction == 'ns':
                sx = emo.location['northing'] - nmean
            
            ax.plot(sx, -1 * emo.location['elevation'] - 7,
                    marker='v', ms=7, color='k')
            
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
    
def plot_station_loop(emo_dir, save_dir=None, fig_type='png'):
    """
    plot all stations in a directory from the .emo file
    
    :param emo_dir: DESCRIPTION
    :type emo_dir: TYPE
    :param save_dir: DESCRIPTION, defaults to None
    :type save_dir: TYPE, optional
    :return: DESCRIPTION
    :rtype: TYPE

    """
    
    if not isinstance(emo_dir, Path):
        emo_dir = Path(emo_dir)
        
    if save_dir is not None:
        if not isinstance(save_dir, Path):
            save_dir = Path(save_dir)
    else:
        save_dir = emo_dir
        
    for folder in emo_dir.iterdir():
        if folder.is_dir():
            emo_fn = list(folder.glob('*.emo'))[-1]
        emo_obj = TEMEMO(emo_fn)
        emo_obj.read_emo_file()
        fig, ax1, ax2 = emo_obj.plot(title=folder.name)
        fig.savefig(save_dir.joinpath(f"{folder.name}.{fig_type}"), dpi=300,
                    bbox_inches='tight')
        print(f'\t-> Plotted {folder.name}')
           
def create_survey_summary(smooth_dir, blocky_dir):
    """
    creat a csv file of the models  
    :param emo_dir: DESCRIPTION
    :type emo_dir: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """
    
    emo_list = []
    for emo_dir in [Path(smooth_dir), Path(blocky_dir)]:
        for emo_fn in get_emo_files_from_dir(emo_dir):
            name = emo_fn.parts[-2]
            emo_obj = TEMEMO(emo_fn)
            emo_obj.read_emo_file()
            entry = {'name': name, 
                     'collection_date': '', 
                     'collected_by': 'GMEGSC-USGS',
                     'easting': emo_obj.location['easting'],
                     'northing': emo_obj.location['northing'],
                     'elevation': emo_obj.location['elevation'],
                     'utm_zone': '11N',
                     'loop_size': 100,
                     'damping_resistor': 440,
                     'model_type': emo_dir.name,
                     'model_date': emo_obj.model_date,
                     'doi_relative': emo_obj.doi_relative.mean(),
                     'doi_absolute': emo_obj.doi_absolute.mean(),
                     'rms_data': emo_obj.norms.iloc[-1].data,
                     'rms_total': emo_obj.norms.iloc[-1].total}
            for res_key in [col for col in emo_obj.model.columns if 'res' in col]:
                entry[res_key.replace('res', 'resistivity')] = emo_obj.model[res_key].iloc[-1]
                
            for thick_key in [col for col in emo_obj.model.columns if 'thic' in col]:
                entry[thick_key.replace('thic', 'thickness')] = emo_obj.model[thick_key].iloc[-1]
            emo_list.append(entry)
    return pd.DataFrame(emo_list)
        
# =============================================================================
# test
# =============================================================================
# fn = r"c:\Users\peaco\Documents\MT\UM2020\TEM\Models\blocky\T00\_1_1.ml.emo"
# t = TEMEMO(fn)
# l = t.read_emo_file()
# f, ax1, ax2 = t.plot(title="TEM00")

# plot_station_loop(r"c:\Users\peaco\Documents\MT\UM2020\TEM\Models\smooth",
#                   r"c:\Users\peaco\Documents\MT\UM2020\TEM\Models\Figures\smooth")

df = create_survey_summary(r"c:\Users\peaco\Documents\MT\UM2020\TEM\Models\smooth",
                           r"c:\Users\peaco\Documents\MT\UM2020\TEM\Models\blocky")
df.to_csv(r"c:\Users\peaco\Documents\MT\UM2020\TEM\survey_summary.csv", index=False)
# line_name = '30'
# # line = ['T20', 'T21', 'T22', 'T23', 'T24', 'T25']
# line = ['T07', 'T08', 'T00', 'T09', 'T10']
# # line = ['T00', 'T01', 'T02', 'T03', 'T04', 'T05']
# line = ['T11', 'T12', 'T13', 'T14']

# line = ['T30', 'T31', 'T32']
# tem_dir = Path(r"c:\Users\peaco\Documents\MT\UM2020\TEM\Models")

# for mtype in ['smooth', 'blocky']:
#     model_dir = tem_dir.joinpath(mtype)
    
#     emo_fn_list = get_emo_files_from_dir(model_dir,
#                                          stations=line) 
    
#     emo_collection = EMOCollection(emo_fn_list)
#     emo_collection.profile_direction = 'ns'
#     ax1, fig1 = emo_collection.plot(dx=5, 
#                                     dz=60,
#                                     method='linear',
#                                     res_limits=(1, 3.5),
#                                     cmap=mtcolors.mt_rd2gr2bl,
#                                     xpad=-60,
#                                     ypad=30)
    
#     fig1.savefig(tem_dir.joinpath('Figures', 
#                                   f"um_tem_line_{line_name}_{mtype}.pdf"),
#                  dpi=300, bbox_inches='tight')
    
#     fig1.savefig(tem_dir.joinpath('Figures',
#                                   f"um_tem_line_{line_name}_{mtype}.png"),
#                  dpi=300, bbox_inches='tight')
