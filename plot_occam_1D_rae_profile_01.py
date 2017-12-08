# -*- coding: utf-8 -*-
"""
Created on Tue Dec 05 15:17:55 2017

@author: jpeacock
"""

import os
import mtpy.modeling.occam1d as occam1d
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

dir_path = r"d:\Peacock\MTData\Umatilla\EDI_Files_birrp\Edited"
station_list = ['hf{0:02}'.format(ii) for ii in [70, 5, 71, 48, 49]]
iter_num = 6

plt.rcParams['font.size'] = 8

fig = plt.figure(dpi=300)
for ii, ss in enumerate(station_list):
    iter_fn = os.path.join(dir_path, ss, 'Det_{0}.iter'.format(iter_num))
    model_fn = os.path.join(dir_path, ss, 'Model1D')
    m_obj = occam1d.Model()
    m_obj.read_iter_file(iter_fn, model_fn)
    
    ax = fig.add_subplot(1, len(station_list), ii+1) 
    ax.set_title(ss.upper(), fontdict={'size':11, 'weight':'bold'})
    ax.plot(10**m_obj.model_res[:, 1], m_obj.model_depth*3.28084, ls='steps-')
    
    ax2 = plt.twinx(ax)
    ax2.plot(10**m_obj.model_res[:, 1], m_obj.model_depth, ls='None')
    
    ax.set_xscale('log')
    ax.xaxis.set_ticks([1, 10, 100, 1000])
    ax.grid(which='both', alpha=.7, color=(.75, .75, .75))

    ax.set_xlim(1, 1000)
    ax.set_ylim(1000*3.28084, 0)

    ax.yaxis.set_major_locator(MultipleLocator(300))
    ax.yaxis.set_minor_locator(MultipleLocator(50))
    
    
    ax2.set_ylim(1000, 0)
    ax2.yaxis.set_major_locator(MultipleLocator(100))
    ax2.yaxis.set_minor_locator(MultipleLocator(10))

    
#    ax.set_xlabel('Resistivity (Ohm-m)', 
#                  fontdict={'size':10, 'weight':'medium'})
    
    ax2.set_ylim(1000, 0)

    if ii == 0:
        ax.set_ylabel('Depth (ft)', 
                      fontdict={'size':10, 'weight':'medium'})
        ax2.tick_params(labelleft='off', labelright='off', 
                       right='off', left='off')
    elif ii == len(station_list)-1:
        ax2.set_ylabel('Depth (m)', 
                  fontdict={'size':10, 'weight':'medium'})
        ax.tick_params(labelleft='off', labelright='off', 
                       right='off', left='off')
    
    else:
        ax.tick_params(labelleft='off', labelright='off', 
                       right='off', left='off')
        
        ax2.tick_params(labelleft='off', labelright='off', 
                       right='off', left='off')
    if ii == 2:
        ax.set_xlabel('Resistivity (Ohm-m)', 
                      fontdict={'size':10, 'weight':'medium'})
plt.show()

#fig.savefig(os.path.join(dir_path, 'rae_profile_01.png'.format(ss)), dpi=600)
#plt.close('all')
    