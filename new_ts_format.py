# -*- coding: utf-8 -*-
"""
Created on Thu Jul 06 14:24:18 2017

@author: jpeacock
"""

#==============================================================================
# Imports
#==============================================================================
import os
import time

import tables
import mtpy.usgs.zen as zen

#==============================================================================

fn = r"d:\Peacock\MTData\Umatilla\hf05\hf05_20170517_193018_256_EX.Z3D" 
#==============================================================================
class MT_TS(object):
    """
    MT time series object that will read/write data in different formats
    including hdf5, txt, miniseed.
    
    Metadata
    -----------
    
        ==================== ==================================================
        Name                 Description        
        ==================== ==================================================
        azimuth              clockwise angle from coordinate system N (deg)
        calibration_fn       file name for calibration data
        component            component name [ 'ex' | 'ey' | 'hx' | 'hy' | 'hz']
        coordinate_system    [ geographic | geomagnetic ]
        datum                datum of geographic location ex. WGS84
        declination          geomagnetic declination (deg)
        dipole_length        length of dipole
        ==================== ==================================================
    
    .. note:: Currently only supports hdf5 and text files
    """


z1 = zen.Zen3D(fn)
z1.read_z3d()
z1.station = '{0}{1}'.format(z1.metadata.line_name, z1.metadata.rx_xyz0[0:2])

h5_fn = fn[0:-4]+'.h5'
pd_h5_fn = fn[0:-4]+'_pd.h5' 

if not os.path.exists(h5_fn):

    z1_h5 = tables.open_file(h5_fn, mode='w', title='Test')
    ts_arr = z1_h5.create_array('/', 'time_series', z1.convert_counts())
    
    ts_arr.attrs.station = z1.station
    ts_arr.attrs.sampling_rate = int(z1.df)
    ts_arr.attrs.start_time_epoch_sec = time.mktime(time.strptime(z1.zen_schedule, 
                                                                  zen.datetime_fmt))
    ts_arr.attrs.start_time_utc = z1.zen_schedule
    ts_arr.attrs.n_samples = int(z1.time_series.size)
    ts_arr.attrs.component = z1.metadata.ch_cmp
    ts_arr.attrs.coordinate_system = 'geomagnetic'
    ts_arr.attrs.dipole_length = float(z1.metadata.ch_length)
    ts_arr.attrs.azimuth = float(z1.metadata.ch_azimuth)
    ts_arr.attrs.units = 'mV'
    ts_arr.attrs.lat = z1.header.lat
    ts_arr.attrs.lon = z1.header.long
    ts_arr.attrs.datum = 'WGS84'
    ts_arr.attrs.data_logger = 'Zonge Zen'
    ts_arr.attrs.instrument_num = None
    ts_arr.attrs.calibration_fn = None
    ts_arr.attrs.declination = 3.6
    
    z1_h5.close()
    
#if not os.path.exists(pd_h5_fn):
#
#    cols = pd.MultiIndex.from_product([[z1.station], 
#                                       [int(z1.df)]],
#                                      names=['station', 
#                                             'sampling_rate'])
#
#    z1_df = pd.DataFrame(data=z1.convert_counts(), columns=cols)
#    
#    z1_store = pd.HDFStore(pd_h5_fn, 'w')
#    z1_store.put('time_series', z1_df)
#        
##    z1_store.get_storer('time_series').attrs.station = z1.station
##    z1_store.get_storer('time_series').attrs.sampling_rate = int(z1.df)
##    z1_store.get_storer('time_series').attrs.start_time_epoch_sec = time.mktime(time.strptime(z1.zen_schedule, 
##                                                                  zen.datetime_fmt))
##    z1_store.get_storer('time_series').attrs.start_time_utc = z1.zen_schedule
##    z1_store.get_storer('time_series').attrs.n_samples = int(z1.time_series.size)
##    z1_store.get_storer('time_series').attrs.component = z1.metadata.ch_cmp
##    z1_store.get_storer('time_series').attrs.coordinate_system = 'geomagnetic'
##    z1_store.get_storer('time_series').attrs.dipole_length = float(z1.metadata.ch_length)
##    z1_store.get_storer('time_series').attrs.azimuth = float(z1.metadata.ch_azimuth)
##    z1_store.get_storer('time_series').attrs.units = 'mV'
##    z1_store.get_storer('time_series').attrs.lat = z1.header.lat
##    z1_store.get_storer('time_series').attrs.lon = z1.header.long
##    z1_store.get_storer('time_series').attrs.datum = 'WGS84'
##    z1_store.get_storer('time_series').attrs.instrument = 'Zonge Zen'
##    z1_store.get_storer('time_series').attrs.calibration_fn = None
##    z1_store.get_storer('time_series').attrs.declination = 3.6
#    
#    z1_store.close()


#store = pd.HDFStore(h5_fn, 'r')


