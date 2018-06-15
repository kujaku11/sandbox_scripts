# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
import pandas as pd
import numpy as np
import mtpy.utils.configfile as configfile
import mtpy.usgs.usgs_cache as usgs_cache

# =============================================================================
# Functions to help analyze config files
# =============================================================================
def check_data(database, name):
    
    if database.notes[0] == 'None':
        database.notes[0] = ''
    elif database.notes[0][-1] != ';':
        database.notes[0] += ';'
    # check start times
    column_bool = database.columns.str.contains(name)
    name_labels = database.columns[column_bool].tolist()
    value_arr = np.array(database[database.columns[column_bool]],
                         dtype=np.int).flatten()
    test = np.array([value_arr[0] == value_arr[ii] for ii in range(value_arr.size)])
    if not (test == True).sum() == test.size:
        
        tf_dict = dict(zip(*np.unique(test, return_counts=True))) 
        
        if tf_dict[True] > tf_dict[False]:
            for comp, test in zip(name_labels, test):
                if test == False:
                    database.notes[0] += ' {0} is off;'.format(comp)
        elif tf_dict[True] < tf_dict[False]:
            for comp, test in zip(name_labels, test):
                if test == True:
                    database.notes[0] += ' {0} is off;'.format(comp)
    return database

def check_std(database, tol=.005):
    """
    check standard deviation for bad data
    """
    if database.notes[0] == 'None':
        database.notes[0] = ''
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
        database = check_data(database, name)
    database = check_std(database)
# =============================================================================
# test the function
# =============================================================================
cfg_dir = r"c:\Users\jpeacock\Documents\imush\G016"

cfg_fn_list = sorted([os.path.join(cfg_dir, fn) for fn in os.listdir(cfg_dir)
                      if 'mtft24' not in fn])

count = 0
for cfg_fn in cfg_fn_list:
    cfg_dict = configfile.read_configfile(cfg_fn)
    if count == 1:
        cfg_db = check_db(pd.DataFrame([cfg_dict[cfg_dict.keys()[0]]]))
        
        count += 1
    else:
        cfg_db.append(check_db(pd.DataFrame([cfg_dict[cfg_dict.keys()[0]]])))
