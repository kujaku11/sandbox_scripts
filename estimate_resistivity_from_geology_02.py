# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 10:55:45 2019

@author: jpeacock
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import json

# =============================================================================
# Inputs
# =============================================================================
fn = r"c:\Users\jpeacock\OneDrive - DOI\Geysers\resistivity_sampling_points_inv06.csv"
cmap = 'Blues'

f_bins = np.logspace(0, 3, num=200)

rock_dict = {'fsp':'fsp - Franciscan Serpentinite',
             'fgw':'fgw - Franciscan graywacke',
             'Qtb':'Qtb - basalt Caldwell Pines',
             'fmgw':'fmgw - Franciscan Metagraywacke', 
             'fsrgw': 'fsrgw - Franciscan graywacke Melange',
             'Qls': 'Qls - landslide deposits', 
             'fgs': 'fgs - Franciscan Greenstone',
             'fsch': 'fsch - Franciscan Schist',
             'Qt': 'Qt - terrace deposits', 
             'fch': 'fch - Franciscan Chert',
             'KJgv': 'KJgv - Great Valley Sequence', 
             'Qal': 'Qal - alluvium',
             'abm': 'Qabm - andesite Bogg Mountain',
             'KJf':'KJf - Franciscan Assemblage', 
             'Qc': 'Qc - Coalluvium',
             'Qdcf': 'Qdcf - rhyodacite Cobb Mountain',
             'Qraf': 'Qraf - rhyolite flows Alder Creek',
             'mum':'fmum - metamorphic ultra-mafics', 
             'Qf': 'Qf - Fill Deposits', 
             'Jos': 'Jos - Coast Range Ophiolite',
             'Qsc': 'Qsc - silica carbonate',
             'Qdcv':'Qdcv - dacite Cobb Valley',
             'Qvc':'Qvc - rhyodacite flows and domes Cobb Mountain',
             'Qmt':'Qmt - mine tailings'}

depth_dict = {'fgw':(None, 700),
              'Qf':(0, 3000)}
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


def get_best_distribution(data):
    dist_names = ["norm", "exponweib", "weibull_max", "weibull_min",
                  "pareto", "genextreme", "lognorm"]
    dist_results = []
    params = {}
    for dist_name in dist_names:
        dist = getattr(stats, dist_name)
        param = dist.fit(data)

        params[dist_name] = param
        # Applying the Kolmogorov-Smirnov test
        D, p = stats.kstest(data, dist_name, args=param)
        print("p value for "+dist_name+" = "+str(p))
        dist_results.append((dist_name, p))

    # select the best fitted distribution
    best_dist, best_p = (max(dist_results, key=lambda item: item[1]))
    # store the name of the best fit and its p value

    print("Best fitting distribution: "+str(best_dist))
    print("Best p value: "+ str(best_p))
    print("Parameters for the best fit: "+ str(params[best_dist]))

    return best_dist, best_p, params[best_dist]

def get_layer_depth(layer_name):
    """
    get the layer depth from given name
    """
    find_01 = layer_name.find('_') + 1
    if layer_name.count('m') > 1:
        find_02 = layer_name.find('m', 4)
        find_01 += 1
        scale = -1
    else:
        find_02 = layer_name.find('m')
        scale = 1
    depth = int(layer_name[find_01:find_02]) * scale
    return depth

def get_layers(layer_list, depth):
    """
    get only the layers for the given geology
    """
    
    layer_dict = dict([(layer, get_layer_depth(layer)) for layer in layer_list])
    return_list = []
    if depth[0] is None:
        for layer, l_depth in layer_dict.items():
            if l_depth <= depth[1]:
                return_list.append(layer)
    else:
        for layer, l_depth in layer_dict.items():
            if l_depth >= depth[0] and l_depth <= depth[1]:
                return_list.append(layer)
                
    return return_list
        
        
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

dist_dict = {}
for rock_type in rock_types[1:]:
    rock_df = df[df.Code == rock_type]
    try:
        depth_range = depth_dict[rock_type]
    except KeyError:
        depth_range = depth_dict['fgw']
    rock_layers = get_layers(layers, depth_range)
    res_df = rock_df[rock_layers]
    res_df = res_df.where(res_df < 10)
    res = 10**res_df.stack().values
    
    best_dist, best_p, params = get_best_distribution(res)
    dist_dict[rock_type] = {'best_dist':best_dist}
     
     
    
#    fig = plt.figure(1)
#    fig.clf()
#    ax = fig.add_subplot(1, 1, 1)
#    n_values, res_bins, res_patches = ax.hist(res, 
#                                              bins=f_bins,
#                                              density=1)
#    ax.set_xscale('log')
#
#    
#    # To normalize your values
#    col = (n_values - n_values.min()) / (n_values.max() - n_values.min())
#    for c, p in zip(col, res_patches):
#        plt.setp(p, 'facecolor', cm(c))
#
#    ### plot fitting log normal plot    
#    res_lognorm, res_sigma = fit_lognorm(res_bins[:-1], res)
#    
#    
#    res_mlk = res_bins[np.where(res_lognorm == res_lognorm.max())][0]
#    res_lk, = ax.plot([res_mlk, res_mlk], [0, 1], 
#                         lw=3, ls=':', color='k')
#    res_max, = ax.plot([res_mlk + res_sigma, res_mlk+res_sigma], [0, 1], 
#                         lw=3, ls=':', color=(.5, .5, .5))
#    
#    f_index = np.where(res_lognorm == res_lognorm.max())[0][0]
#    f_min = res_lognorm[np.where(f_bins <= res_mlk+res_sigma)][-1]
#    try:
#        f_min = f_bins[np.where(res_lognorm[0:f_index] <= f_min)[0][-1]]
#        res_min, = ax.plot([f_min,f_min], [0, 1], 
#                           lw=3, ls=':', color=(.5, .5, .5))
#    except IndexError:
#        print('Something wrong with min in {0}'.format(rock_type))
#        pass
#    
#    ax.plot(res_bins[:-1], res_lognorm, color=(.96, .6, 0), lw=2)
#    
#    ax.set_xlim(1, 1000)
#    ax.set_ylim(0, res_lognorm.max()*1.5)
#    ax.set_xlabel('Resistivity ($\Omega \cdot m$)', fontdict={'size':10})
#    ax.set_ylabel('Normalized Amplitude', fontdict={'size':10})
#    
#    fig.suptitle(rock_dict[rock_type])
#    
#    l2, = ax.plot([None, None], [None, None], 'b', ls='none')
#    res_mlk_data = res_bins[np.where(n_values == n_values.max())][0]
#    ax.legend([res_lk, res_min, l2], 
#              ['fit mode = {0:<5.4g} $\Omega \cdot m$'.format(res_mlk),
#               'fit std = {0:<5.4g} $\Omega \cdot m$'.format(res_sigma),
#               'data mode = {0:<5.4g} $\Omega \cdot m$'.format(res_mlk_data)],
#               loc='upper left')
#
#    
#    plt.show()
#    fig.savefig(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\inv_06_{0}_res.png".format(rock_type),
#                dpi=1200)
#    
#    res_dict['rock_type'].append(rock_type)
#    res_dict['mode'].append(res_mlk)
#    res_dict['std'].append(res_sigma)
#    
#rdf = pd.DataFrame(res_dict)
#rdf.to_csv(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\rock_resistivity_summary.csv",
#           index=False)
with open(r"c:\Users\jpeacock\OneDrive - DOI\Geysers\distributions.json", 'w') as fid:
    json.dump(dist_dict, fid)