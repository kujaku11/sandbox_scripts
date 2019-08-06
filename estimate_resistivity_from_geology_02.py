# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 10:55:45 2019

@author: jpeacock
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# =============================================================================
# Inputs
# =============================================================================
fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\resistivity_sampling_points.csv"
cmap = 'Blues'

f_bins = np.logspace(0, 3, num=200)

rock_dict = {'fsp':'fsp - Franciscan Serpentinite',
             'fgw':'fgw - Franciscan Greywacke',
             'Qtb':'Qtb - Caldwell Pines',
             'fmgw':'fmgw - Franciscan Metagreywacke', 
             'fsrgw': 'fsrgw - Franciscan Greywackey',
             'Qls': 'Qls', 
             'fgs': 'fgs - Franciscan Greenstone',
             'fsch': 'fsch - Franciscan Schist',
             'Qt': 'Qt', 
             'fch': 'fch - Franciscan Chert',
             'KJgv': 'KJgv - Great Valley', 
             'Qal': 'Qal',
             'abm': 'abm',
             'KJf':'KJf', 
             'Qc': 'Qc',
             'Qdcf': 'Qdcf',
             'Qraf': 'Qraf',
             'mum':'metamorphic ultra-mafics', 
             'Qf': 'Qf - Felsite', 
             'Jos': 'Jos - Ophiolite',
             'Qsc': 'Qsc'}
# =============================================================================
#  define fit a log normal distribution to data
# =============================================================================
def fit_lognorm(x_data, y_data):
    """
    fit lognormal
    """
    shape, loc, scale = stats.lognorm.fit(y_data)

    pdf = stats.lognorm.pdf(x_data, shape, loc, scale)
    
    s = shape**2
    mu = np.log(scale)
    
    fwhm = np.exp((mu - s) + np.sqrt(2 * s * np.log(2))) - \
           np.exp((mu - s) - np.sqrt(2 * s * np.log(2)))
           
    return pdf, shape*fwhm

# =============================================================================
# Start script
# =============================================================================
cm = plt.cm.get_cmap(cmap)

### read in csv
df = pd.read_csv(fn)
rock_types = df.Code.unique()
layers = [col for col in df.columns if 'gz_' in col]

res_dict = {'rock_type':[],
            'mode':[],
            'std':[]}

for rock_type in rock_types[1:]:
    rock_df = df[df.Code == rock_type]
    res_df = rock_df[layers]
    res_df = res_df.where(res_df < 10)
    res = 10**res_df.stack().values
    
    fig = plt.figure(1)
    fig.clf()
    ax = fig.add_subplot(1, 1, 1)
    n_values, res_bins, res_patches = ax.hist(res, 
                                              bins=f_bins,
                                              density=1)
    ax.set_xscale('log')

    
    # To normalize your values
    col = (n_values - n_values.min()) / (n_values.max() - n_values.min())
    for c, p in zip(col, res_patches):
        plt.setp(p, 'facecolor', cm(c))

    ### plot fitting log normal plot    
    res_lognorm, res_sigma = fit_lognorm(res_bins[:-1], res)
    
    
    res_mlk = res_bins[np.where(res_lognorm == res_lognorm.max())][0]
    res_lk, = ax.plot([res_mlk, res_mlk], [0, 1], 
                         lw=3, ls=':', color='k')
    res_max, = ax.plot([res_mlk + res_sigma, res_mlk+res_sigma], [0, 1], 
                         lw=3, ls=':', color=(.5, .5, .5))
    
    f_index = np.where(res_lognorm == res_lognorm.max())[0][0]
    f_min = res_lognorm[np.where(f_bins <= res_mlk+res_sigma)][-1]
    try:
        f_min = f_bins[np.where(res_lognorm[0:f_index] <= f_min)[0][-1]]
        res_min, = ax.plot([f_min,f_min], [0, 1], 
                           lw=3, ls=':', color=(.5, .5, .5))
    except IndexError:
        print('Something wrong with min in {0}'.format(rock_type))
        pass
    ax.plot(res_bins[:-1], res_lognorm, color=(.96, .6, 0), lw=2)
    
    ax.set_xlim(1, 1000)
    ax.set_ylim(0, res_lognorm.max()*1.5)
    ax.set_xlabel('Resistivity ($\Omega \cdot m$)', fontdict={'size':10})
    ax.set_ylabel('Normalized Amplitude', fontdict={'size':10})
    
    fig.suptitle(rock_dict[rock_type])
    
    ax.legend([res_lk, res_min], 
              ['mode = {0:<5.4g} $\Omega \cdot m$'.format(res_mlk),
               'std = {0:<5.4g} $\Omega \cdot m$'.format(res_sigma)],
               loc='upper right')

    
    plt.show()
    fig.savefig(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\{0}_res.png".format(rock_type),
                dpi=1200)
    
    res_dict['rock_type'].append(rock_type)
    res_dict['mode'].append(res_mlk)
    res_dict['std'].append(res_sigma)
    
rdf = pd.DataFrame(res_dict)
rdf.to_csv(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\rock_resistivity_summary.csv",
           index=False)
