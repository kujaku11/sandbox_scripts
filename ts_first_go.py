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
import numpy as np
import mtpy.usgs.zen as zen
import pandas as pd

#==============================================================================

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
        dipole_length        length of dipole (m)
        data_logger          data logger type
        instrument_id        ID number of instrument for calibration
        lat                  latitude of station in decimal degrees
        lon                  longitude of station in decimal degrees
        n_samples            number of samples in time series
        sampling_rate        sampling rate in samples/second
        start_time_epoch_sec start time in epoch seconds
        start_time_utc       start time in UTC
        station              station name
        units                units of time series
        ==================== ==================================================
    
    .. note:: Currently only supports hdf5 and text files
    """
    
    def __init__(self, **kwargs):
        
        self.station = 'mt00'
        self.sampling_rate = 1
        self.start_time_epoch_sec = 0.0
        self.start_time_utc = '1980-01-01,00:00:00'
        self.n_samples = 0
        self.component = None
        self.coordinate_system = 'geomagnetic'
        self.dipole_length = 0
        self.azimuth = 0
        self.units = 'mV'
        self.lat = 0.0
        self.lon = 0.0
        self.datum = 'WGS84'
        self.data_logger = 'Zonge Zen'
        self.instrument_id = None
        self.calibration_fn = None
        self.declination = 0.0
        self.ts = None 
        self.fn_hdf5 = None
        self.fn_ascii = None
        
        self._attr_list = ['station',
                           'sampling_rate',
                           'start_time_epoch_sec',
                           'start_time_utc',
                           'n_samples',
                           'component',
                           'coordinate_system',
                           'dipole_length',
                           'azimuth',
                           'units',
                           'lat', 
                           'lon',
                           'datum',
                           'data_logger',
                           'instrument_id',
                           'calibration_fn',
                           'declination']
        
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
        
        
    def write_hdf5(self, fn_hdf5, ts=None):
        """
        Write a hdf5 time series file
        
        Arguments
        ---------------
            **fn_hdf5** : string
                          full path to save hdf5 file
                          
            **ts** : numpy.ndarray (n_samples)
                     time series data 
                     
        """
        
        
        self.fn_hdf5 = fn_hdf5
        if ts is not None:
            self.ts = ts
            
        if self.ts is None:
            raise MT_TS_Error('Time series is None')
        
        # check to see if a file already exists, it doesn't like it when
        # one already does
        if os.path.exists(self.fn_hdf5) is True:
            print('{0} already exists'.format(self.fn_hdf5))
            delete_bool = input('Delete old file (True/False):\n')
            if delete_bool == True:
                os.remove(self.fn_hdf5)
            else:
                print('Did not overwrite {0}'.format(self.fn_hdf5))
                return 
        
        # create the hdf5 object
        self.hdf5_obj = tables.open_file(self.fn_hdf5, mode='w', title='Test')
        
        # make a time series array        
        ts_arr = self.hdf5_obj.create_array('/', 'time_series', self.ts)
        
        # add attributes
        ts_arr.attrs.station = self.station
        ts_arr.attrs.sampling_rate = self.sampling_rate
        ts_arr.attrs.start_time_epoch_sec = self.start_time_epoch_sec 
        ts_arr.attrs.start_time_utc = self.start_time_utc
        ts_arr.attrs.n_samples = self.n_samples
        ts_arr.attrs.component = self.component
        ts_arr.attrs.coordinate_system = self.coordinate_system
        ts_arr.attrs.dipole_length = self.dipole_length
        ts_arr.attrs.azimuth = self.azimuth
        ts_arr.attrs.units = self.units
        ts_arr.attrs.lat = self.lat
        ts_arr.attrs.lon = self.lon
        ts_arr.attrs.datum = self.datum
        ts_arr.attrs.data_logger = self.data_logger
        ts_arr.attrs.instrument_id = self.instrument_id
        ts_arr.attrs.calibration_fn = self.calibration_fn
        ts_arr.attrs.declination = self.declination
        
        self.hdf5_obj.close()
        
        print('    Wrote time series to {0}'.format(self.fn_hdf5))
        
    def read_hdf5(self, fn_hdf5):
        """
        read in an hdf5 file and fill attributes accordingly
        """
        self.fn_hdf5 = fn_hdf5        
        
        if not os.path.isfile(self.fn_hdf5):
            raise MT_TS_Error('Could not find {0}'.format(self.fn_hdf5))

        self.hdf5_obj = tables.open_file(self.fn_hdf5, 'r')
        
        self.ts = self.hdf5_obj.get_node('/', 'time_series')
        
        self.station = self.ts.attrs.station
        self.sampling_rate = self.ts.attrs.sampling_rate
        self.start_time_epoch_sec = self.ts.attrs.start_time_epoch_sec
        self.start_time_utc = self.ts.attrs.start_time_utc
        self.n_samples = self.ts.attrs.n_samples
        self.component = self.ts.attrs.component
        self.coordinate_system = self.ts.attrs.coordinate_system
        self.dipole_length = self.ts.attrs.dipole_length
        self.azimuth = self.ts.attrs.azimuth
        self.units = self.ts.attrs.units
        self.lat = self.ts.attrs.lat
        self.lon = self.ts.attrs.lon
        self.datum = self.ts.attrs.datum
        self.data_logger = self.ts.attrs.data_logger
        self.instrument_id = self.ts.attrs.instrument_id
        self.calibration_fn = self.ts.attrs.calibration_fn
        self.declination = self.ts.attrs.declination
        
        print 'Read in {0}'.format(self.fn_hdf5)
        
    def write_hdf5_pandas(self, fn_hdf5):
        """
        use pandas to write the hdf5 file
        """        
        
        self.fn_hdf5 = fn_hdf5
        
        df = pd.DataFrame(np.array(self.ts))
        
        hdf5_store = pd.HDFStore(self.fn_hdf5, 'w')
        hdf5_store['time_series'] = df
        
        # add in attributes
        hdf5_store.get_storer('time_series').attrs.station = self.station
        hdf5_store.get_storer('time_series').attrs.sampling_rate = self.sampling_rate
        hdf5_store.get_storer('time_series').attrs.start_time_epoch_sec = self.start_time_epoch_sec 
        hdf5_store.get_storer('time_series').attrs.start_time_utc = self.start_time_utc
        hdf5_store.get_storer('time_series').attrs.n_samples = self.n_samples
        hdf5_store.get_storer('time_series').attrs.component = self.component
        hdf5_store.get_storer('time_series').attrs.coordinate_system = self.coordinate_system
        hdf5_store.get_storer('time_series').attrs.dipole_length = self.dipole_length
        hdf5_store.get_storer('time_series').attrs.azimuth = self.azimuth
        hdf5_store.get_storer('time_series').attrs.units = self.units
        hdf5_store.get_storer('time_series').attrs.lat = self.lat
        hdf5_store.get_storer('time_series').attrs.lon = self.lon
        hdf5_store.get_storer('time_series').attrs.datum = self.datum
        hdf5_store.get_storer('time_series').attrs.data_logger = self.data_logger
        hdf5_store.get_storer('time_series').attrs.instrument_id = self.instrument_id
        hdf5_store.get_storer('time_series').attrs.calibration_fn = self.calibration_fn
        hdf5_store.get_storer('time_series').attrs.declination = self.declination
        
        hdf5_store.flush()
        hdf5_store.close()
        
    def read_hdf5_pandas(self, fn_hdf5):
        """
        read using pandas
        """
        
        self.fn_hdf5 = fn_hdf5

        hdf5_store = pd.HDFStore(self.fn_hdf5, 'r')
        
        self.ts = hdf5_store['time_series']
        
        for attr in self._attr_list:
            value = getattr(hdf5_store.get_storer('time_series').attrs, attr)
            setattr(self, attr, value)
            
        hdf5_store.close()

                
        
    def write_ascii_file(self, fn_ascii=None, chunk_size=4096):
        """
        write an ascii format file
        """
        
        st = time.time()
        if fn_ascii is not None:
            self.fn_ascii = fn_ascii
        
        if self.fn_ascii is None:
            self.fn_ascii = self.fn_hdf5[:-2]+'txt'
            
        if self.ts is None:
            self.read_hdf5(self.fn_hdf5)

        # get the number of chunks to write        
        chunks = self.ts.shape[0]/chunk_size
            
        # make header lines
        header_lines = ['# MT time series text file for {0}'.format(self.station)]
        header_lines += ['# {0} = {1}'.format(attr, getattr(self, attr)) 
                        for attr in sorted(self._attr_list)]

        # write to file in chunks
        with open(self.fn_ascii, 'w') as fid:
            # write header lines first
            fid.write('\n'.join(header_lines))
    
            # write time series indicator
            fid.write('\n# *** time_series ***\n')
            
            # write in chunks
            for cc in range(chunks):
                # changing the dtype of the array is faster than making
                # a list of strings
                try:
                    ts_lines = np.array(self.ts[cc*chunk_size:(cc+1)*chunk_size][0],
                                        dtype='S20')
                except IndexError:
                    ts_lines = np.array(self.ts[cc*chunk_size:(cc+1)*chunk_size],
                                        dtype='S20')
                fid.write('\n'.join(list(ts_lines)))
                # be sure to write a new line after each chunk otherwise
                # they run together
                fid.write('\n')
             
            # be sure to write the last little bit
            try:
                fid.write('\n'.join(list(np.array(self.ts[(cc+1)*chunk_size:][0],
                                                  dtype='S20'))))
            except IndexError:
                fid.write('\n'.join(list(np.array(self.ts[(cc+1)*chunk_size:],
                                                  dtype='S20'))))
                
        # get an estimation of how long it took to write the file    
        et = time.time()
        time_diff = et-st
        
        print '--> Wrote {0}'.format(self.fn_ascii)
        print '    Took {0:.2f} seconds'.format(time_diff)

        
        
                
#==============================================================================
# Error classes
#==============================================================================
class MT_TS_Error(Exception):
    pass        
 
#==============================================================================
#  Testing
#==============================================================================

fn = r"d:\Peacock\MTData\Umatilla\hf05\hf05_20170517_193018_256_EX.Z3D" 
## TEST Writing
z1 = zen.Zen3D(fn)
z1.read_z3d()
z1.station = '{0}{1}'.format(z1.metadata.line_name, z1.metadata.rx_xyz0[0:2])

h5_fn = fn[0:-4]+'03.h5' 

#h5_fn = r"d:\Peacock\MTData\Umatilla\hf05\hf05_20170517_193018_256_EX.h5"
test_ts = MT_TS()

test_ts.ts = z1.convert_counts()
test_ts.station = z1.station
test_ts.sampling_rate = int(z1.df)
test_ts.start_time_epoch_sec = time.mktime(time.strptime(z1.zen_schedule, 
                                                              zen.datetime_fmt))
test_ts.start_time_utc = z1.zen_schedule
test_ts.n_samples = int(z1.time_series.size)
test_ts.component = z1.metadata.ch_cmp
test_ts.coordinate_system = 'geomagnetic'
test_ts.dipole_length = float(z1.metadata.ch_length)
test_ts.azimuth = float(z1.metadata.ch_azimuth)
test_ts.units = 'mV'
test_ts.lat = z1.header.lat
test_ts.lon = z1.header.long
test_ts.datum = 'WGS84'
test_ts.data_logger = 'Zonge Zen'
test_ts.instrument_num = None
test_ts.calibration_fn = None
test_ts.declination = 3.6

test_ts.write_hdf5_pandas(h5_fn)
#
read_ts = MT_TS()
read_ts.read_hdf5_pandas(h5_fn)

#read_ts = MT_TS()
#read_ts.read_hdf5(h5_fn)
#
#read_ts.write_ascii_file()



