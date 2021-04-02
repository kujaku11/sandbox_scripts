# -*- coding: utf-8 -*-
"""
Created on Wed Jun 07 18:24:13 2017

@author: jpeacock-pr
"""

import os
import numpy as np
import mtpy.core.mt as mt
import scipy.interpolate as spi
import scipy.signal as sps
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
#import mtpy.imaging.mtcolors as mtcolors

#edi_path = r"c:\MT\Umatilla\EDI_Files_birrp"
#edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
#            if edi.endswith('.edi') and 'um' in edi]+\
#           [r"c:\MT\Umatilla\EDI_Files_birrp\hf45.edi"]

edi_path = r"c:\Users\jpeacock-pr\Google Drive\FieldWork\Camas_EDI_Files"
edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi')]


plt.rcParams['font.size'] = 9  

for jj, f in enumerate(range(0, 60, 4)):
#for jj, f in enumerate([10]):

    ns = len(edi_list)
    lat_arr = np.zeros(ns)
    lon_arr = np.zeros(ns)
    res_arr = np.zeros(ns)
    
    for ii, edi in enumerate(edi_list):
        mt_obj = mt.MT(edi)
        lat_arr[ii] = mt_obj.lat
        lon_arr[ii] = mt_obj.lon
#        res_arr[ii] = (mt_obj.Z.phase[f, 0, 1]+mt_obj.Z.phase[f, 1, 0]+180)/2
#        res_arr[ii] = np.rad2deg(np.arctan2(mt_obj.Z.det[0][f].imag, mt_obj.Z.det[0][f].real))
#        res_arr[ii] = np.abs(mt_obj.Z.det[f])/mt_obj.Z.freq[f]*0.2
        res_arr[ii] = np.abs(mt_obj.Z.det[f])/mt_obj.Z.freq[f]*0.2
        
    x = np.linspace(lon_arr.min(), lon_arr.max(), 100)
    y = np.linspace(lat_arr.min(), lat_arr.max(), 100)
    points = np.array([lon_arr, lat_arr])
    
    grid_x, grid_y = np.meshgrid(x, y)
    
    res_map = spi.griddata(points.T, 
                           res_arr, 
                           (grid_x, grid_y), 
                           method='cubic' )
                           
    
    
    fig = plt.figure(dpi=150)
    fig.clf()
    fig.subplots_adjust(left=.07, right=.95, top=.99, bottom=.07)
    ax = fig.add_subplot(1, 1, 1, aspect='equal')
#    im = ax.imshow(sps.medfilt2d(res_map, kernel_size=(1, 1)), 
#                   extent=(lon_arr.min(),
#                           lon_arr.max(), 
#                           lat_arr.min(), 
#                           lat_arr.max()), 
#                  origin='lower',
#                  cmap='jet',
#                  vmin=0,
#                  vmax=90)
    im = ax.imshow(sps.medfilt2d(np.log10(res_map), kernel_size=(1, 1)), 
                   extent=(lon_arr.min(),
                           lon_arr.max(), 
                           lat_arr.min(), 
                           lat_arr.max()), 
                  origin='lower',
                  cmap='jet_r',
                  vmin=.3,
                  vmax=2.7)
    ax.scatter(lon_arr, lat_arr, marker='v', c='k')
    ax.set_xlabel('Longitude (deg)', fontdict={'size':10, 'weight':'bold'})
    ax.set_ylabel('Latitude (deg)', fontdict={'size':10, 'weight':'bold'})
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.xaxis.set_major_locator(MultipleLocator(.05))
    ax.yaxis.set_major_locator(MultipleLocator(.05))
    plt.colorbar(im, ax=ax, shrink=.6, )
    
    plt.show()
    fig.savefig(r"c:\MT\Camas\res_zyx_maps\{0:02}_{1:.4g}_res.png".format(jj, 1./mt_obj.Z.freq[f]))
    plt.close()
    