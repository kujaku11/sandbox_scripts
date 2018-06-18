# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
import pandas as pd
import numpy as np
import mtpy.utils.configfile as configfile

# =============================================================================
# Functions to help analyze config files
# =============================================================================
def check_data(database, name):
    """
    check the columns with base name to make sure all values are equal
    """
    if database.notes[0] in [None, 'none', 'None']:
        database.notes[0] = ''
    elif database.notes[0] == '':
        pass
    elif database.notes[0][-1] != ';':
        database.notes[0] += ';'
    # check start times
    column_bool = database.columns.str.contains(name)
    name_labels = database.columns[column_bool].tolist()
    value_arr = np.array(database[database.columns[column_bool]],
                         dtype=np.int).flatten()
    test = np.array([value_arr[0] == value_arr[ii] for ii in range(value_arr.size)])
    if not (test == True).sum() == test.size:
        
        #tf_dict = dict(zip(*np.unique(test, return_counts=True))) 
        
#        if tf_dict[True] > tf_dict[False]:
        if test[0] == True and (test[1:] == False).sum() == test[1:].size:
            database.notes[0] += ' {0} is off;'.format(name_labels[0])
        else:
            for comp, test in zip(name_labels, test):
                if test == False:
                    database.notes[0] += ' {0} is off;'.format(comp)
#        elif tf_dict[True] < tf_dict[False]:
#            for comp, test in zip(name_labels, test):
#                if test == True:
#                    database.notes[0] += ' {0} is off;'.format(comp)
    return database

def check_std(database, tol=.005):
    """
    check standard deviation for bad data
    """
    if database.notes[0] in [None, 'none', 'None']:
        database.notes[0] = ''
    elif database.notes[0] == '':
        pass
    elif database.notes[0][-1] != ';':
        database.notes[0] += ';'
        
    column_bool = database.columns.str.contains('_std')
    name_labels = database.columns[column_bool].tolist()
    value_arr = np.array(database[database.columns[column_bool]],
                         dtype=np.float).flatten()
    for name, value in zip(name_labels, value_arr):
        if value > tol:
            database.notes[0] += ' {0} is large;'.format(name)
    
    return database

def check_db(database):
    """
    convinience function to check all values in database
    """
    for key in ['_start', '_nsamples']:
        database = check_data(database, key)
    database = check_std(database)
    
    return database
# =============================================================================
# test the function
# =============================================================================
#station_dir = r"c:\Users\jpeacock\Documents\imush"
station_dir = r"/mnt/hgfs/MTData/iMUSH_Zen_samples/imush"

s_count = 0
for station in os.listdir(station_dir):
    cfg_dir = os.path.join(station_dir, station)
    if not os.path.isdir(cfg_dir):
        continue
    if station in ['H020']:
        continue
    
    cfg_fn_list = sorted([os.path.join(cfg_dir, fn) for fn in os.listdir(cfg_dir)
                          if 'mt' not in fn and 'runs' not in fn 
                          and fn.endswith('.cfg')])
    
    count = 0
    for cfg_fn in cfg_fn_list:
        cfg_dict = configfile.read_configfile(cfg_fn)
        if count == 0:
            cfg_db = check_db(pd.DataFrame([cfg_dict[cfg_dict.keys()[0]]]))
            count += 1
        else:
            cfg_db = cfg_db.append(check_db(pd.DataFrame([cfg_dict[cfg_dict.keys()[0]]])))
            count += 1
    
    cfg_db.to_csv(os.path.join(cfg_dir, '{0}_runs.csv'.format(station)),
                  index=False)

    # make a single file that summarizes
    #(1) site name
    #(2) siteID
    #(3) lat
    #(4) lon
    #(5) national map elevation
    #(6) Hx azimuth
    #(7) Ex azimuth
    #(8) start date [yyyymmdd]
    #(9) Ex dipole length [m]
    #(10) Ey dipole length [m]
    #(11) wideband channels
    #(12) long period channel
    station_dict = pd.compat.OrderedDict()
    station_dict['site_name'] = station
    station_dict['siteID'] = station
    station_dict['lat'] = cfg_db.lat.astype(np.float).mean()
    station_dict['lon'] = cfg_db.lon.astype(np.float).mean()
    station_dict['nm_elev'] = cfg_db.elev.astype(np.float).mean()
    station_dict['hx_azm'] = cfg_db.hx_azm.astype(np.float).median()
    station_dict['ex_azm'] = cfg_db.ex_azm.astype(np.float).median()
    station_dict['start_date'] = cfg_db.start_date.min().split('T')[0].replace('-', '')
    station_dict['ex_len'] = cfg_db.ex_len.astype(np.float).median()
    station_dict['ey_len'] = cfg_db.ey_len.astype(np.float).median()
    station_dict['wb'] = cfg_db.n_chan.astype(np.int).median()
    station_dict['lp'] = 0
    
    #(1) site name
    #(2) lat
    #(3) lon
    #(4) national map elevation
    #(5) start date
    #(6) end date
    #(7) instrument type [W = wideband, L = long period]
    #(8) quality factor from 1-5 [5 is best]
    loc_dict = pd.compat.OrderedDict()
    loc_dict['site_name'] = station
    loc_dict['lat'] = cfg_db.lat.astype(np.float).mean()
    loc_dict['lon'] = cfg_db.lon.astype(np.float).mean()
    loc_dict['nm_elev'] = cfg_db.elev.astype(np.float).mean()
    loc_dict['start_date'] = cfg_db.start_date.min().split('T')[0].replace('-', '')
    loc_dict['stop_date'] = cfg_db.stop_date.max().split('T')[0].replace('-', '')
    loc_dict['instrument'] = 'W'
    loc_dict['quality'] = 5
    
    if s_count == 0:
        s_db = pd.DataFrame([station_dict])
        l_db = pd.DataFrame([loc_dict])
        s_count += 1
    else:
        s_db = s_db.append(pd.DataFrame([station_dict]))
        l_db = l_db.append(pd.DataFrame([loc_dict]))
        s_count += 1 

s_db.to_csv(os.path.join(station_dir, 'station_info.csv'.format(station)),
            index=False)
l_db.to_csv(os.path.join(station_dir, 'location_info.csv'.format(station)),
            index=False)