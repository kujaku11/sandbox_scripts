# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 10:03:20 2019

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import os
import numpy as np
import struct
import datetime
import dateutil

import pandas as pd

# =============================================================================
# class objects
# =============================================================================
class GPS(object):
    """
    class to hold gps stamps
    """
    
    def __init__(self, gps_string):
        
        self.gps_string = gps_string
        self.type_dict = {'gprmc':{0:'type', 
                                   1:'time', 
                                   2:'fix',
                                   3:'latitude',
                                   4:'latitude_hemisphere',
                                   5:'longitude',
                                   6:'longitude_hemisphere',
                                   7:'skip',
                                   8:'skip',
                                   9:'date',
                                   10:'declination',
                                   11:'declination_hemisphere'},
                          'gpgga':{0:'type', 
                                   1:'time', 
                                   2:'latitude',
                                   3:'latitude_hemisphere',
                                   4:'longitude',
                                   5:'longitude_hemisphere',
                                   6:'var_01',
                                   7:'var_02',
                                   8:'var_03',
                                   9:'elevation',
                                   10:'elevation_units',
                                   11:'elevation_error',
                                   12:'elevation_error_units'}}
        self.parse_gps_string()
        
    def parse_gps_string(self):
        """
        parse a gps string
        """
        if isinstance(self.gps_string, bytes):
            gps_list = self.gps_string.strip().split(b',')
            gps_list = [value.decode() for value in gps_list[0:12]]
        else:
            gps_list = self.gps_string.strip().split(',')[0:12]
        
        attr_dict = self.type_dict[gps_list[0].lower()]
            
        for index, value in enumerate(gps_list):
            setattr(self, '_'+attr_dict[index], value)
            
    @property
    def latitude(self):
        """
        Latitude in decimal degrees, WGS84
        """
        index = len(self._latitude) - 7
        lat = float(self._latitude[0:index]) + float(self._latitude[index:])/60
        if 's' in self._latitude_hemisphere.lower():
            lat *= -1
        return lat
        
    @property
    def longitude(self):
        """
        Latitude in decimal degrees, WGS84
        """
        index = len(self._longitude) - 7
        lon = float(self._longitude[0:index]) + float(self._longitude[index:])/60
        if 'w' in self._longitude_hemisphere.lower():
            lon *= -1
        return lon
        
    @property
    def elevation(self):
        """
        elevation in meters
        """
        if hasattr(self, '_elevation'):
            return float(self._elevation)
        else:
            return None
        
    @property
    def time_stamp(self):
        """
        return a datetime object of the time stamp
        """
        if hasattr(self, '_date'):
            return dateutil.parser.parse('{0} {1}'.format(self._date, self._time),
                                         dayfirst=True)
        else:
            return dateutil.parser.parse('{0} {1}'.format('010180', self._time),
                                         dayfirst=True) 
        
    @property
    def declination(self):
        """
        geomagnetic declination in degrees from north
        """
        if hasattr(self, '_declination'):
            dec = float(self._declination)
            if 'w' in self._declination_hemisphere.lower():
                dec *= -1
            return dec
        else:
            return None
        
    @property
    def fix(self):
        """
        GPS fixed
        """
        if hasattr(self, '_fix'):
            return self._fix
        else:
            return None

class NIMSHeader(object):
    """
    class to hold the NIMS header
    """
    
    def __init__(self, fn=None):
        self.fn = fn
        self._max_header_length = 1000
        self.header_dict = None
        self.site_name = None
        self.state_province = None
        self.country = None
        self.box_id = None
        self.mag_id = None
        self.ex_length = None
        self.ex_azimuth = None
        self.ey_length = None
        self.ey_azimuth = None
        self.n_electrode_id = None
        self.s_electrode_id = None
        self.e_electrode_id = None
        self.w_electrode_id = None
        self.ground_electrode_info = None
        self.header_gps_stamp = None
        self.header_gps_latitude = None
        self.header_gps_longitude = None
        self.header_gps_elevation = None
        self.operator = None
        self.comments = None
        self.run_id = None
        self.data_start_seek = 0
        
        
    def read_header(self, fn=None):
        """
        read header information
        """
        if fn is not None:
            self.fn = fn
            
        if not os.path.exists(self.fn):
            raise NIMSError('Could not find file {0}'.format(self.fn))
            
        ### load in the entire file, its not too big
        with open(self.fn, 'rb') as fid:
            header_str = fid.read(self._max_header_length)
            header_list = header_str.split(b'\r')
            
        self.header_dict = {}
        for line in header_list[0:-1]:
            line = line.decode()
            if line.find('>') == 0:
                continue
            elif line.find(':') > 0:
                key, value = line.split(':', 1)
                self.header_dict[key.strip().lower()] = value.strip()
            elif line.find('<--') > 0:
                value, key = line.split('<--')
                self.header_dict[key.strip().lower()] = value.strip()  
        data_start_byte = header_list[-1].strip()[0:1]
        self.data_start_seek = header_str.find(data_start_byte)
        
        self.parse_header_dict()
    
    def parse_header_dict(self, header_dict=None):
        """
        parse the header dictionary into something useful
        """
        if header_dict is not None:
            self.header_dict = header_dict
            
        assert isinstance(self.header_dict, dict)
        
        for key, value in self.header_dict.items():
            if 'wire' in key:
                if key.find('n') == 0:
                    self.ex_length = float(value.split()[0])
                    self.ex_azimuth = float(value.split()[1])
                elif key.find('e') == 0:
                    self.ey_length = float(value.split()[0])
                    self.ey_azimuth = float(value.split()[1])
            elif 'system' in key:
                self.box_id = value.split(';')[0]
                self.mag_id = value.split(';')[1]
            elif 'gps' in key:
                gps_list = value.split()
                self.header_gps_stamp = dateutil.parser.parse(' '.join(gps_list[0:2]),
                                                              dayfirst=True)
                self.header_gps_latitude = self._get_latitude(gps_list[2], gps_list[3])
                self.header_gps_longitude = self._get_longitude(gps_list[4], gps_list[5])
                self.header_gps_elevation = float(gps_list[6])
            elif 'run' in key:
                self.run_id = value.replace('"', '')
            else:
                setattr(self, key.replace(' ', '_').replace('/','_'), value)
    
    def _get_latitude(self, latitude, hemisphere):
        if not isinstance(latitude, float):
            latitude = float(latitude)
        if hemisphere.lower() == 'n':
            return latitude
        if hemisphere.lower() == 's':
            return -1*latitude

    def _get_longitude(self, longitude, hemisphere):
        if not isinstance(longitude, float):
            longitude = float(longitude)
        if hemisphere.lower() == 'e':
            return longitude
        if hemisphere.lower() == 'w':
            return -1*longitude
        
class NIMS(NIMSHeader):
    """
    read NIMS data
    """
    
    def __init__(self, fn=None):

        super().__init__(fn)
        self.block_size = 131
        self.sampling_rate = 8 ### samples/second
        self.e_conversion_factor = 2.44141221047903e-06
        self.h_conversion_factor = 0.01
        self.t_conversion_factor = 70
        self.t_offset = 18048
        self._int_max = 8388608
        self._int_factor = 16777216
        self._block_dict = {'soh':0,
                            'block_len':1,
                            'status':2,
                            'gps':3,
                            'sequence':4,
                            'elec_temp':(5, 6),
                            'box_temp':(7, 8),
                            'logic':81,
                            'end':130}
        self.info_array = None
        self.data_array = None
        
        self.indices = self.make_index_values()
        
        if self.fn is not None:
            self.read_nims()
        
    def make_index_values(self):
        """
        Index values for the channels recorded
        """
        ### make an array of index values for magnetics and electrics
        indices = np.zeros((8,5), dtype=np.int)
        for kk in range(8):
            ### magnetic blocks
            for ii in range(3):
                indices[kk, ii] = 9 + (kk) * 9 + (ii) * 3
            ### electric blocks
            for ii in range(2):
                indices[kk, 3+ii] = 82 + (kk) * 6 + (ii) * 3
        return indices
    
    def get_gps_list(self, nims_string):
        """
        get a list of GPS strings from the main string
        """
            
        ### read in GPS strings into a list to be parsed later
        gps_str = [struct.unpack('c', 
                                 nims_string[ii*self.block_size+3:ii*self.block_size+4])[0]
                 for ii in range(int(len(nims_string)/self.block_size))]
        gps_str = b''.join(gps_str)
        
        gps_str_list = gps_str.replace(b'\xd9', b'').replace(b'\xc7', b'').split(b'$')
        gps_str_list = [stamp[0:stamp.find(b'*')].decode() for stamp in gps_str_list]
        ### check the first few stamps
        if gps_str_list[0].find('$') == -1:
            gps_str_list = gps_str_list[1:]
            
        match = [gps_str_list[ii].split(',')[1] == gps_str_list[ii-1].split(',')[1] 
                 for ii in range(1, 6)]
        first_stamp_index = np.where(np.array(match) == True)[0][0]
        gps_list = [GPS(stamp_str) for stamp_str in gps_str_list[first_stamp_index:]]
        
        ### match up the GPRMC and GPGGA together
        self.gps_list = []
        for ii in range(len(gps_list)):
            time_stamp = gps_list[ii].time_stamp
            match_list = [gps_list[ii]]
            for stamp in gps_list[ii+1:ii+3]:
                if stamp.time_stamp.time() == time_stamp.time():
                    match_list.append(stamp)
                    break
            if len(match_list) == 2:
                self.gps_list.append(match_list)
            else:
                continue
        
        
    def get_gps_stamp_indices(self):
        """
        get the index location of the stamps
        """
        
        index_values = np.where(self.info_array['status'] == 0)[0]
        stamps = np.zeros_like(index_values)
        for ii in range(index_values.size):
            if index_values[ii] - index_values[ii-1] == 1:
                continue
            else:
                stamps[ii] = index_values[ii]
        stamps = stamps[np.nonzero(stamps)]
        
        return stamps
    
    def get_gps_stamps(self):
        """
        make an array of gps stamps with index values
        """
        
        stamp_indices = self.get_gps_stamp_indices()
        gps_stamps = [[index, stamps] for index, stamps in zip(stamp_indices,
                      self.gps_list)]
        return gps_stamps
                  
    def read_nims(self, fn=None):
        """
        read nims binary file
        """
        if fn is not None:
            self.fn = fn

        ### read in header information and get the location of end of header
        self.read_header()
        
        ### load in the entire file, its not too big, start from the 
        ### end of the header information.
        with open(self.fn, 'rb') as fid:
            fid.seek(self.data_start_seek)
            data_str = fid.read()
        
        ### get GPS stamps from the binary string first
        self.get_gps_list(data_str)
        
        ### read in full string as unsigned integers
        data = np.frombuffer(data_str, dtype=np.uint8)
        
        ### check the size of the data, should have an equal amount of blocks
        if (data.size % self.block_size) == 0:
            data = data.reshape((int(data.size/self.block_size), 
                                 self.block_size))
        else:
            print('odd number of bytes, not even blocks')
        
        ### need to parse the data
        ### first get the status information
        self.info_array = np.zeros(data.shape[0],
                                   dtype=[('soh', np.int),
                                          ('block_len', np.int),
                                          ('status', np.int),
                                          ('gps', np.int),
                                          ('sequence', np.int),
                                          ('elec_temp', np.float),
                                          ('box_temp', np.float),
                                          ('logic', np.int),
                                          ('end', np.int)])    
        
        for key, index in self._block_dict.items():
                    if 'temp' in key:
                        value = ((data[:, index[0]] * 256 + data[:, index[1]]) - \
                                 self.t_offset)/self.t_conversion_factor
                    else:
                        value = data[:, index]
                    self.info_array[key][:] = value
                    
        ### get GPS stamps with index values
        self.stamps = self.get_gps_stamps()
         
        ### get data
        self.data_array = np.zeros(data.shape[0]*self.sampling_rate,
                                   dtype=[('hx', np.float),
                                          ('hy', np.float), 
                                          ('hz', np.float),
                                          ('ex', np.float),
                                          ('ey', np.float)])
        
        ### fill the data
        for cc, comp in enumerate(['hx', 'hy', 'hz', 'ex', 'ey']):
            channel_arr = np.zeros((data.shape[0], 8), dtype=np.float)
            for kk in range(self.sampling_rate):
                index = self.indices[kk, cc]
                value = (data[:, index]*256 + data[:, index+1]) * np.array([256]) + \
                        data[:, index+2]
                value[np.where(value > self._int_max)] -= self._int_factor
                channel_arr[:, kk] = value
            self.data_array[comp][:] = channel_arr.flatten()
            
        ### clean things up
        ### I guess that the E channels are opposite phase?
        for comp in ['ex', 'ey']:
            self.data_array[comp] *= -1
            
        self.align_data()
            
            
    def align_data(self):
        """
        Need to match up the first good GPS stamp with the data
        
        Do this by using the first GPS stamp and cutting all data before that.
        
        put the data into a pandas data frame that is indexed by time
        """
        
        ### first GPS stamp within the data is at a given index that is 
        ### assumed to be the number of seconds from the start of the run.
        ### therefore cut out 8 * index values from the data
        
        first_index = self.stamps[0][0]
        bad_data = first_index * self.sampling_rate
        print('cutting {0} points from the beginning of the time series'.format(bad_data))
        
        self.data_array = self.data_array[bad_data:]
        
#        self.data_df = pd.Dataframe(self.data_array, index)
            
        
            
# =============================================================================
# Exceptions
# =============================================================================
class NIMSError(Exception):
    pass
    
#### need to align gps stamps
# =============================================================================
# Test
# =============================================================================

#nims_fn = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\FieldWork\LP_Data\Mnp310a\DATA.BIN"
nims_fn = r"c:\Users\jpeacock\Downloads\data_rgr022c.bnn"
st = datetime.datetime.now()
nims_obj = NIMS(nims_fn)
#nims_obj.read_header(nims_fn)

et = datetime.datetime.now()

tdiff = et - st
print('Took {0} seconds'.format(tdiff.total_seconds()))
