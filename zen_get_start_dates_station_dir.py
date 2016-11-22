# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 09:38:25 2016

@author: jpeacock
"""

import mtpy.usgs.zen as zen
import os
import numpy as np
import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator

datetime_fmt = '%Y-%m-%d,%H:%M:%S'
datetime_display = '%m-%d, %H:%M:%S'

survey_path = r"d:\Peacock\MTData\MonoBasin\MB_June2015"

plot = True

date_dict = {}
rr_dict = {}
for station in os.listdir(survey_path):
    station_path = os.path.join(survey_path, station)
    if os.path.isdir(station_path) is True:
        fn_list = [os.path.join(station_path, fn) 
                   for fn in os.listdir(station_path)
                   if fn.lower().endswith('ex.z3d')]
        
        if len(fn_list) == 0:
            print 'No Z3D files found in folder: {0} '.format(station)
            continue

        station_date_arr = np.zeros(len(fn_list), dtype=[('df', np.float),
                                                         ('start_dt', '|S20')])
        for f_index, fn in enumerate(fn_list):
            zd = zen.Zen3D(fn)
            zd.read_all_info()
            station_date_arr[f_index]['df'] = zd.df
            station_date_arr[f_index]['start_dt'] = zd.zen_schedule
            try:
                rr_dict[zd.zen_schedule]    
            except KeyError:
                rr_dict[zd.zen_schedule] = []
                
            rr_dict[zd.zen_schedule].append((station, zd.df))
                
        if len(np.nonzero(station_date_arr)[0]) != 0:
            date_dict[station] = station_date_arr[np.nonzero(station_date_arr['df'])]

#---------------------------------------------
# print out in a useful way

lines = []
for key in sorted(rr_dict.keys()):
    k_list = key.split(',')    
    k_date = k_list[0]
    k_time = k_list[1]
    lines.append('Date: {0}, Time: {1}'.format(k_date, k_time))
    lines.append('-'*60)
    for k_tuple in rr_dict[key]:
        lines.append('\tStation: {0}, Sampling Rate: {1:.0f}'.format(k_tuple[0],
                     k_tuple[1]))
                     
    lines.append('='*60)
with open(os.path.join(survey_path, 'Remote_Reference_List.txt'), 'w') as fid:
    fid.write('\n'.join(lines))



#-------------------------------------

if plot is True:
    plt.rcParams['font.size'] = 14
    
    df_dict = {4096:(.7, .1, 0), 1024:(.5, .5, 0), 256:(0, .2, .8)}                       
    # plot the results is a compeling graph
    fig = plt.figure(2, [12, 10])
    ax = fig.add_subplot(1, 1, 1)
    all_dates = []
    y_labels = ['', '']
    
    for k_index, key in enumerate(sorted(date_dict.keys())):
        y_labels.append(key)
        for ii, k_arr in enumerate(date_dict[key]):
            x_date_0 = datetime.datetime.strptime(k_arr['start_dt'], datetime_fmt)
            try:
                x_date_1 = datetime.datetime.strptime(date_dict[key]['start_dt'][ii+1],
                                                      datetime_fmt)
            except IndexError:
                x_date_1 = x_date_0
            
            y_values = [k_index, k_index]
            
            l1, = ax.plot([x_date_0, x_date_1], y_values,
                          lw=8, color=df_dict[k_arr['df']])
    

    fig.autofmt_xdate(rotation=60)
    ax.xaxis.set_major_formatter(mdates.DateFormatter(datetime_display))
    ax.xaxis.set_major_locator(MultipleLocator((1)))
    ax.xaxis.set_minor_locator(MultipleLocator((.25)))
    ax.xaxis.set_tick_params(width=2, size=5)
    xlim = ax.get_xlim()
   
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_ticklabels(y_labels)
    ax.yaxis.set_tick_params(width=2, size=5)
    ax.set_ylim(-1, len(y_labels)-2)
    
    ax.grid(which='major', linestyle='--', color=(.7, .7, .7)) 
    ax.set_axisbelow(True)
    
    l_4096 = plt.Line2D([0, 1], [0, 0], lw=8, color=df_dict[4096])
    l_1024 = plt.Line2D([0, 1], [0, 0], lw=8, color=df_dict[1024])
    l_256 = plt.Line2D([0, 1], [0, 0], lw=8, color=df_dict[256])
  
    fig.legend([l_4096, l_1024, l_256], ['4096', '1024', '256'], ncol=3,
               loc='upper center')
                         
    plt.show()