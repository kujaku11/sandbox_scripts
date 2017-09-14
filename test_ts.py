# -*- coding: utf-8 -*-
"""
Created on Thu Jul 06 14:24:18 2017

@author: jpeacock
"""

#==============================================================================
# Imports
#==============================================================================
#import os
#import time

import numpy as np
#import mtpy.usgs.zen as zen
#import pandas as pd
import mtpy.core.ts as mtts
reload(mtts)

#============================================================================
fn = r"c:\Users\jrpeacock\Documents\GitHub\processing\test_data\mb311_20170308_150518_256.EX"

# read header
with open(fn, 'r') as fid:
    header_line = fid.readline()

header_list = header_line[1:].strip().split()

# read in data, this is extremely slow
data = np.loadtxt(fn, skiprows=1)
n = data.size

# new file
h5_fn = r"c:\Users\jrpeacock\test_no_index_09.h5"

#==============================================================================
# Fill ts 
#==============================================================================
test_ts = mtts.MT_TS()

test_ts.ts = data
test_ts.station = header_list[0]
test_ts.component = header_list[1]
test_ts.sampling_rate = float(header_list[2])
test_ts.start_time_epoch_sec = float(header_list[3])
test_ts.n_samples = int(header_list[4])
test_ts.units = header_list[5]
test_ts.lat = float(header_list[6])
test_ts.lon = float(header_list[7])
test_ts.elev = float(header_list[8])
test_ts.coordinate_system = 'geomagnetic'
test_ts.dipole_length = 100.
test_ts.azimuth = 0
test_ts.datum = 'WGS84'
test_ts.data_logger = 'Zonge Zen'
test_ts.instrument_num = None
test_ts.calibration_fn = None
test_ts.declination = 3.6

# write file
test_ts.write_hdf5(h5_fn, compression_level=9)

test_ts.estimate_spectra(**{'nperseg':2**10})


#
#read_ts = mtts.MT_TS()
#read_ts.read_hdf5(h5_fn)

#read_ts = MT_TS()
#read_ts.read_hdf5(h5_fn)
#
#read_ts.write_ascii_file()



