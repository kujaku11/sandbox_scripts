# -*- coding: utf-8 -*-
"""

Created on Fri Jul 31 15:59:45 2020

:author: Jared Peacock

:license: MIT

"""

from pathlib import Path
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import MultipleLocator, ScalarFormatter

# =============================================================================
# 
# =============================================================================
class TEMEMO():
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
        self.location = {'easting': 0, 'northing': 0, 'elevation': 0}
        self.doi_relative = 0
        self.doi_absolute = 0
        
        self.channel_dict = {1: 'HM-RC005',
                             2: 'HM-RC200',
                             3: 'LM-RC005',
                             4: 'LM-RC200'}
        
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
            raise ValueError(f'File {self.fn} does not exist')
            
        lines = self.fn.read_text().split('\n')
        model_index = 0
        for ii, line in enumerate(lines):
            if line.startswith('Model #'):
                model_index = ii
                break
        print(f'Model Index = {model_index}') 
        # can't fucking parse the header cause its not standard, just store
        # as a list of strings.
        self.model_parameters = lines[0:model_index - 1]
        
        max_iter = int(lines[model_index - 1].strip().split()[0])
        
        self.location = dict([(k, float(v)) for k, v in zip(['easting', 'northing', 'elevation'],
                                                     lines[model_index + 1].strip().split()[2:])])
        
        # read model
        cols = ['iter'] + lines[model_index + 3].strip().lower().replace('#', '').split()
        model_iterations = dict([(col, []) for col in cols])
        
        for ii in range(max_iter):
            values = lines[model_index + 4 + ii].strip().split()
            for k, v in zip(cols, values):
                model_iterations[k].append(float(v))
                
        model_iterations = dict([(k, v) for k, v in model_iterations.items()
                                 if len(v) > 1])
        m_index = [int(ii) for ii in model_iterations.pop('iter')]
        self.model = pd.DataFrame(model_iterations, 
                                  index=m_index)

        # read data
        data_index = 0
        for ii, line in enumerate(lines[model_index + max_iter:], model_index+max_iter):
            if line.startswith('Data'):
                data_index = ii
                break
        print(f"Data Index = {data_index}")
        data_header = lines[data_index + 2].strip().replace('#', '').lower().split()
        data = dict([(key, []) for key in data_header])
        for line in lines[data_index+ 3:]:
            if 'data' in line.lower():
                continue
            values = line.strip().split()
            if len(values) > 6:
                for k, v in zip(data_header, values):
                    data[k].append(float(v))
                    
        self.data = pd.DataFrame(data)
        
        # get DOI
        self.doi_absolute = [float(ii) for ii in lines[-4].strip().split()]
        self.doi_relative = [float(ii) for ii in lines[-2].strip().split()]
        
    def plot(self, fig_num=1, iteration=None, res_limits=[10, 5000], 
             title=None):
        """
        plot data and models
        """
        if iteration is None:
            iteration = sorted([col for col in self.data.columns if 'ite' in col])[-1]
            print(f'Using iteration column: {iteration}')
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
            l1, = ax_t.loglog(data.time, data.inp_data,
                           color=(1/ds, 0, 0), 
                           ls='-',
                           marker='o',
                           ms=2,
                           lw=.5)
            data_lines.append(l1)
            data_labels.append(f"Data {self.channel_dict[int(ds)]}")
            
            # plot response
            l2, = ax_t.loglog(data.time, data[iteration],
                           color=(0, 0, 1/ds), 
                           ls='None',
                           marker='+',
                           ms=6)
            resp_lines.append(l2)
            resp_labels.append(f"Resp {self.channel_dict[int(ds)]}")
            
        # make legend
        ax_t.legend(data_lines + resp_lines, 
                    data_labels + resp_labels,
                    loc='lower left',
                    ncol=1,
                    fontsize=7)
        
        # plot depth
        res_keys = [col for col in self.model.columns if 'res' in col]
        thick_keys = [col for col in self.model.columns if 'thic' in col]
        plot_res = self.model.iloc[-1][res_keys].values
        
        plot_depth = self.model.iloc[-1][thick_keys].values
        plot_depth = [0] + [plot_depth[0:ii].sum() for ii in range(plot_depth.size)]
        plot_depth = np.array(plot_depth) - self.location['elevation']
        
        # plot 
        ax_d.step(plot_res, plot_depth)
        
        # check res limits
        if plot_res.max() > res_limits[1]:
            res_limits[1] = np.round(plot_res.max() ** 1.05, 2)
         
        if plot_res.min() < res_limits[0]:
            res_limits[0] = np.round(plot_res.min() ** .95, 2)
        
        # set axis properties
        ax_d.set_xscale('log')
        ax_d.set_xticks([1, 10, 100, 1000, 10000])
        ax_d.set_xlim(res_limits)
        ax_d.set_ylim((plot_depth.max(), plot_depth.min()))
        ax_d.yaxis.set_minor_locator(MultipleLocator(10))
        ax_d.yaxis.set_major_locator(MultipleLocator(50))
        
        
        # plot doi
        ax_d.fill_between(res_limits, 
                          [self.doi_absolute[0] - self.location['elevation'],
                           self.doi_absolute[0] - self.location['elevation']],
                          [self.doi_absolute[1] - self.location['elevation'],
                           self.doi_absolute[1] - self.location['elevation']],
                          color=(.85, .85, .85),
                          alpha=.85)
        
        ax_d.fill_between(res_limits, 
                          [self.doi_relative[0] - self.location['elevation'],
                           self.doi_relative[0] - self.location['elevation']],
                          [self.doi_relative[1] - self.location['elevation'],
                           self.doi_relative[1] - self.location['elevation']],
                          color=(.7, .7, .7),
                          alpha=.85)
        
        
        # make grid
        for ax in [ax_t, ax_d]:
            ax.grid(which='major', color=(.5, .5, .5), lw=.75, ls='-')
            ax.grid(which='minor', color=(.65, .65, .65), lw=.5, ls='--')
            ax.set_axisbelow(True)
            
        # set axis labels
        f_dict = {'size':12}
        ax_t.set_xlabel('Time [s]', fontdict=f_dict)
        ax_t.set_ylabel(r'$\frac{dB}{dt}$ [$\frac{mV}{A \cdot m^4}$]',
                        fontdict=f_dict)
        ax_d.set_xlabel(r'Resistivity [$\Omega \cdot m$]', fontdict=f_dict)
        ax_d.set_ylabel('Elevation [m]', fontdict=f_dict)
        
        # make tight layout to make things look nice
        fig.tight_layout()
        
        # plot title
        if title is not None:
            fig.suptitle(title)
            fig.subplots_adjust(top=.92)
        
        fig.show()
        
        return fig, ax_t, ax_d

# =============================================================================
# test
# =============================================================================
fn = r"c:\Users\peaco\Documents\MT\UM2020\TEM\Models\blocky\T00\_1_1.ml.emo"
t = TEMEMO(fn)
l = t.read_emo_file()
f, ax1, ax2 = t.plot(title='TEM00')