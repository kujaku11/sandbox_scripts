# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 11:46:10 2018

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

import mtpy.modeling.modem.data as data
import mtpy.modeling.modem.model as model

import mtpy.modeling.occam1d as occam1d
# =============================================================================
# 
# =============================================================================
d_fn = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\modem_inv\inv_02\gv_modem_data_err03.dat"
m_fn = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\modem_inv\inv_02\gv_tip02_cov03_NLCG_031.rho"

occam_path = r"d:\Peacock\MTData\GabbsValley\EDI_Files_birrp\Edited"

elev_fn = r"D:\Peacock\MTData\GabbsValley\gv_elevation.txt"
elev = np.loadtxt(elev_fn,
                  delimiter=',', 
                  dtype={'names':('station', 'elev'),
                         'formats':('S4', np.float)})
# =============================================================================
# Find model location and plot 1D profile
# =============================================================================
d_obj = data.Data()
d_obj.read_data_file(d_fn)

m_obj = model.Model()
m_obj.read_model_file(m_fn)



for s_arr in d_obj.station_locations.station_locations:
    find_east = np.where(m_obj.grid_east >= s_arr['rel_east'])[0][0] - 1
    find_north = np.where(m_obj.grid_north >= s_arr['rel_north'])[0][0] - 1
    
    res_depth = m_obj.res_model[find_north, find_east, :]
    
    # get occam 1D 
    occam_iter_fn = os.path.join(occam_path, 
                                 s_arr['station'].upper(),
                                 'Det_6.iter')
    occam_model_fn = os.path.join(occam_path, 
                                  s_arr['station'].upper(),
                                 'Model1D')
    
    occam1d_model = occam1d.Model()
    occam1d_model.read_iter_file(iter_fn=occam_iter_fn,
                                 model_fn=occam_model_fn)
    res_1d = 10**occam1d_model.model_res[1:, 1]
    depth_1d = occam1d_model.model_depth[1:]
    
    lines = ['# station = {0}'.format(s_arr['station'])]
    lines.append('# lat = {0:.5f}'.format(s_arr['lat']))
    lines.append('# lon = {0:.5f}'.format(s_arr['lon']))
    elev_find = np.where(elev['station'] == s_arr['station'].lower())[0][0]
    lines.append('# elev = {0:.2f} m'.format(elev['elev'][elev_find]))
    lines.append('='*40)
    lines.append('# 3D Resistivity Model')
    lines.append('# depth (m), resistivity (Ohm-m)')
    lines.append('-'*40)
    lines.append('\n'.join(['{0:<12.2f} {1:<12.3f}'.format(d, res) 
                            for d, res in zip(m_obj.grid_z[0:30], 
                                              res_depth[0:30])]))
    lines.append('-'*40)
    lines.append('# 1D Resistivity Model')
    lines.append('# depth (m), resistivity (Ohm-m)')
    lines.append('-'*40)
    lines.append('\n'.join(['{0:<12.2f} {1:<12.3f}'.format(d, res) 
                            for d, res in zip(depth_1d[0:46], 
                                              res_1d[0:46])]))
    txt_fn = r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\depth_profiles\{0}.txt".format(s_arr['station'])
    with open(txt_fn, 'w') as fid:
        fid.write('\n'.join(lines))
#    fig = plt.figure(figsize=[4.5, 8], tight_layout=True)
#    ax = fig.add_subplot(1, 1, 1)
#    l1 = ax.plot(res_depth, m_obj.grid_z[0:-1], ls='steps', color=(0, .45, 1))
#    l2 = ax.plot(res_1d, depth_1d, ls='steps', color=(1, .6, .1))
#    
#    ax.set_xscale('log')
#    ax.set_ylim(2000, 0)
#    ax.set_xlim(.1, 1000)
#    
#    ax.yaxis.set_minor_locator(MultipleLocator(10))
#    ax.yaxis.set_major_locator(MultipleLocator(100))
#    
#    ax.set_xlabel('resistivity (Ohm-m)', fontdict={'size':12, 'weight':'bold'})
#    ax.set_ylabel('depth (m)', fontdict={'size':12, 'weight':'bold'})
#    
#    ax.grid(which='major', linestyle='--', color=(.5, .5, .5))
#    ax.grid(which='minor', linestyle=':', color=(.75, .75, .75))
#    
#    ax.set_title(s_arr['station'], fontsize=12, fontweight='bold')
#    
#    ax.legend([l1[0], l2[0]], ['3D', '1D'], loc='lower left')
#    plt.show()
#    fig.savefig(r"c:\Users\jpeacock\Documents\Geothermal\GabbsValley\depth_profiles\{0}.png".format(s_arr['station']),
#                dpi=600)
#    plt.close('all')