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
import logging

### setup logger
logging.basicConfig(filename='ReadNIMSData.log', 
                    filemode='w', 
                    level=logging.DEBUG,
                    format='%(levelname)s:%(message)s')

# =============================================================================
# class objects
# =============================================================================
class GPSError(Exception):
    pass

class GPS(object):
    """
    class to parse GPS stamp from the NIMS
    
    Depending on the type of Stamp there will be different attributes
    
    GPRMC has full date and time information and declination
    GPGGA has elevation data
    """
    
    def __init__(self, gps_string, index=0):
        
        self.gps_string = gps_string
        self.index = index
        self._time = None
        self._date = '010180'
        self._latitude = None
        self._latitude_hemisphere = None
        self._longitude = None
        self._longitude_hemisphere = None
        self._declination = None
        self._declination_hemisphere = None
        self._elevation = None
        self.valid = False
        self.elevation_units = 'meters'
        
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
                                   11:'declination_hemisphere',
                                   'length':[12],
                                   'type':0, 
                                   'time':1, 
                                   'fix':2,
                                   'latitude':3,
                                   'latitude_hemisphere':4,
                                   'longitude':5,
                                   'longitude_hemisphere':6,
                                   'date':9,
                                   'declination':10},
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
                                   12:'elevation_error_units',
                                   13:'null_01',
                                   14:'null_02',
                                   'length':[14,15],
                                   'type':0, 
                                   'time':1, 
                                   'latitude':2,
                                   'latitude_hemisphere':3,
                                   'longitude':4,
                                   'longitude_hemisphere':5,
                                   'elevation':9,
                                   'elevation_units':10,
                                   'elevation_error':11,
                                   'elevation_error_units':12}}
        self.parse_gps_string(self.gps_string)
        
    def validate_gps_string(self, gps_string):
        """
        make sure the string is valid, remove any binary numbers and find
        the end of the string as '*'
        """
        for replace_str in [b'\xd9', b'\xc7', b'\xcc']:
            gps_string = gps_string.replace(replace_str, b'')
            
        ### sometimes the end is set with a zero for some reason
        gps_string = gps_string.replace(b'\x00', b'*')
        
        if gps_string.find(b'*') < 0:
            logging.error('GPSError: No end to stamp {0}'.format(gps_string))
        else:
            try:
                gps_string = gps_string[0:gps_string.find(b'*')].decode()
                return gps_string
            except UnicodeDecodeError:
                logging.error('GPSError: stamp not correct format, {0}'.format(gps_string))
                return None
        
    def parse_gps_string(self, gps_string):
        """
        parse a gps string
        """
        gps_string = self.validate_gps_string(gps_string)
        if gps_string is None:
            self.valid = False
            return
        
        if isinstance(gps_string, bytes):
            gps_list = gps_string.strip().split(b',')
            gps_list = [value.decode() for value in gps_list]
        else:
            gps_list = gps_string.strip().split(',')
        
        ### validate the gps list to make sure it is usable
        gps_list, error_list = self.validate_gps_list(gps_list)
        if len(error_list) > 0:
            for error in error_list:
                logging.error('GPSError:' + error)
        if gps_list is None:
            return

        attr_dict = self.type_dict[gps_list[0].lower()]
            
        for index, value in enumerate(gps_list):
            setattr(self, '_'+attr_dict[index], value)
            
        if None not in gps_list:
            self.valid = True
            self.gps_string = gps_string
                  
    def validate_gps_list(self, gps_list):
        """
        check to make sure the gps stamp is the correct format
        """
        error_list = []
        try:
            gps_list = self._validate_gps_type(gps_list)
        except GPSError as error:
            error_list.append(error.args[0])
            return None, error_list
        
        ### get the string type
        g_type = gps_list[0].lower()
        
        ### first check the length, if it is not the proper length then
        ### return, cause you never know if everything else is correct
        try:
            self._validate_list_length(gps_list)
        except GPSError as error:
            error_list.append(error.args[0])    
            return None, error_list
        
        try:
            gps_list[self.type_dict[g_type]['time']] = \
                  self._validate_time(gps_list[self.type_dict[g_type]['time']])
        except GPSError as error:
            error_list.append(error.args[0])
            gps_list[self.type_dict[g_type]['time']] = None
            
        try:
            gps_list[self.type_dict[g_type]['latitude']] =\
                self._validate_latitude(gps_list[self.type_dict[g_type]['latitude']],
                                        gps_list[self.type_dict[g_type]['latitude_hemisphere']])
        except GPSError as error:
            error_list.append(error.args[0])
            gps_list[self.type_dict[g_type]['latitude']] = None
        
        try:
            gps_list[self.type_dict[g_type]['longitude']] =\
                self._validate_longitude(gps_list[self.type_dict[g_type]['longitude']],
                                         gps_list[self.type_dict[g_type]['longitude_hemisphere']])
        except GPSError as error:
            error_list.append(error.args[0])
            gps_list[self.type_dict[g_type]['longitude']] = None
        
        if g_type == 'gprmc':
            try:
                gps_list[self.type_dict['gprmc']['date']] =\
                    self._validate_date(gps_list[self.type_dict['gprmc']['date']])
            except GPSError as error:
                error_list.append(error.args[0])
                gps_list[self.type_dict[g_type]['date']] = None
            
        elif g_type == 'gpgga':
            try:
                gps_list[self.type_dict['gpgga']['elevation']] =\
                    self._validate_elevation(gps_list[self.type_dict['gpgga']['elevation']])
            except GPSError as error:
                error_list.append(error.args[0])
                gps_list[self.type_dict['gpgga']['elevation']] = None
            
        return gps_list, error_list
    
    def _validate_gps_type(self, gps_list):
        """Validate gps type should be gpgga or gprmc"""
        gps_type = gps_list[0].lower()
        if 'gpg' in gps_type:
            if len(gps_type) > 5:
                gps_list = ['GPGGA', gps_type[-6:]] + gps_list[1:]
            elif len(gps_type) < 5:
                gps_list[0] = 'GPGGA'
        elif 'gpr' in gps_type:
            if len(gps_type) > 5:
                gps_list = ['GPRMC', gps_type[-6:]] + gps_list[1:]
            elif len(gps_type) < 5:
                gps_list[0] = 'GPRMC'
        
        gps_type = gps_list[0].lower()
        if gps_type not in ['gpgga', 'gprmc']:
            raise GPSError('GPS String type not correct.  '+\
                              'Expect GPGGA or GPRMC, got {0}'.format(gps_type.upper()))
            
        return gps_list
    
    def _validate_list_length(self, gps_list):
        """validate gps list length based on type of string"""
        
        gps_list_type = gps_list[0].lower()
        expected_len = self.type_dict[gps_list_type]['length']
        if len(gps_list) not in expected_len:
            raise GPSError('GPS string not correct length for {0}.  '.format(gps_list_type.upper())+\
                           'Expected {0}, got {1} \n{2}'.format(expected_len, 
                                                              len(gps_list),
                                                              ','.join(gps_list)))
            
    def _validate_time(self, time_str):
        """ validate time string, should be 6 characters long and an int """
        if len(time_str) != 6:
            raise GPSError('Lenght of time string {0} not correct.  '.format(time_str)+\
                           'Expected 6 got {0}'.format(len(time_str)))
        try:
            int(time_str)
        except ValueError:
            raise GPSError('Could not convert time string {0}'.format(time_str))
        
        return time_str
    
    def _validate_date(self, date_str):
        """ validate date string, should be 6 characters long and an int """
        if len(date_str) != 6:
            raise GPSError('Length of date string not correct {0}.  '.format(date_str)+\
                           'Expected 6 got {0}'.format(len(date_str)))
        try:
            int(date_str)
        except ValueError:
            raise GPSError('Could not convert date string {0}'.format(date_str))
        
        return date_str
    
    def _validate_latitude(self, latitude_str, hemisphere_str):
        """validate latitude, should have hemisphere string with it"""
        
        if len(latitude_str) < 8:
            raise GPSError('Latitude string should be larger than 7 characters.  '+\
                           'Got {0}'.format(len(latitude_str)))
        if len(hemisphere_str) != 1:
            raise GPSError('Latitude hemisphere should be 1 character.  '+\
                           'Got {0}'.format(len(hemisphere_str)))
        if hemisphere_str.lower() not in ['n', 's']:
            raise GPSError('Latitude hemisphere {0} not understood'.format(hemisphere_str.upper()))
        try:
            float(latitude_str)
        except ValueError:
            raise GPSError('Could not convert latitude string {0}'.format(latitude_str))
            
        return latitude_str
    
    def _validate_longitude(self, longitude_str, hemisphere_str):
        """validate longitude, should have hemisphere string with it"""
        
        if len(longitude_str) < 8:
            raise GPSError('Longitude string should be larger than 7 characters.  '+\
                           'Got {0}'.format(len(longitude_str)))
        if len(hemisphere_str) != 1:
            raise GPSError('Longitude hemisphere should be 1 character.  '+\
                           'Got {0}'.format(len(hemisphere_str)))
        if hemisphere_str.lower() not in ['e', 'w']:
            raise GPSError('Longitude hemisphere {0} not understood'.format(hemisphere_str.upper()))
        try:
            float(longitude_str)
        except ValueError:
            raise GPSError('Could not convert longitude string {0}'.format(longitude_str))
            
        return longitude_str
    
    def _validate_elevation(self, elevation_str):
        """validate elevation, check for converstion to float"""
        try:
            float(elevation_str)
        except ValueError:
            raise GPSError('Elevation could not be converted {0}'.format(elevation_str))
            
        return elevation_str
                      
    @property
    def latitude(self):
        """
        Latitude in decimal degrees, WGS84
        """
        if self._latitude is not None and self._latitude_hemisphere is not None:
            index = len(self._latitude) - 7
            lat = float(self._latitude[0:index]) + float(self._latitude[index:])/60
            if 's' in self._latitude_hemisphere.lower():
                lat *= -1
            return lat
        else:
            return 0.0
    
    @property
    def longitude(self):
        """
        Latitude in decimal degrees, WGS84
        """
        if self._longitude is not None and self._longitude_hemisphere is not None:
            index = len(self._longitude) - 7
            lon = float(self._longitude[0:index]) + float(self._longitude[index:])/60
            if 'w' in self._longitude_hemisphere.lower():
                lon *= -1
            return lon
        else:
            return 0.0
        
    @property
    def elevation(self):
        """
        elevation in meters
        """
        if self._elevation is not None:
            try:
                return float(self._elevation)
            except ValueError:
                logging.error('GPSError: Could not get elevation GPS string'+\
                              'not complete {0}'.format(self.gps_string))
        else:
            return 0.0
        
    @property
    def time_stamp(self):
        """
        return a datetime object of the time stamp
        """
        if self._time is None:
            return None
        if self._date is None:
            self._date = '010180'
        try:
            return dateutil.parser.parse('{0} {1}'.format(self._date, self._time),
                                         dayfirst=True)
        except ValueError:
            logging.error('GPSError: bad date string {0}'.format(self.gps_string))
            return None
        
    @property
    def declination(self):
        """
        geomagnetic declination in degrees from north
        """
        if self._declination is None or self._declination_hemisphere is None:
            return None
        
        dec = float(self._declination)
        if 'w' in self._declination_hemisphere.lower():
            dec *= -1
        return dec

        
    @property
    def gps_type(self):
        """GPRMC or GPGGA"""
        return self._type
        
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
            
        print('Reading NIMS file {0}'.format(self.fn))
        logging.info('='*72)
        logging.info('Reading NIMS file {0}'.format(self.fn))
            
        ### load in the entire file, its not too big
        with open(self.fn, 'rb') as fid:
            header_str = fid.read(self._max_header_length)
            header_list = header_str.split(b'\r')
            
        self.header_dict = {}
        last_index = len(header_list)
        last_line = header_list[-1]
        for ii, line in enumerate(header_list[0:-1]):
            if ii == last_index:
                break
            if b'comments' in line.lower():
                last_line = header_list[ii+1]
                last_index = ii + 1
                
            line = line.decode()
            if line.find('>') == 0:
                continue
            elif line.find(':') > 0:
                key, value = line.split(':', 1)
                self.header_dict[key.strip().lower()] = value.strip()
            elif line.find('<--') > 0:
                value, key = line.split('<--')
                self.header_dict[key.strip().lower()] = value.strip()
        ### sometimes there are some spaces before the data starts
        if last_line.count(b' ') > 0:
            if last_line[0:1] == b' ':
                last_line = last_line.strip()
            else:
                last_line = last_line.split()[1].strip()
        data_start_byte = last_line[0:1]
        ### sometimes there are rogue $ around
        if data_start_byte in [b'$', b'g']:
            data_start_byte = last_line[1:2]
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
        self.block_sequence = [1, self.block_size]
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
        self.stamps = None
        self.data_df = None
        
        self.indices = self._make_index_values()
        
        if self.fn is not None:
            self.read_nims()
            
    @property
    def latitude(self):
        """
        median latitude value from all the GPS stamps in decimal degrees
        WGS84
        
        Only get from the GPRMC stamp as they should be duplicates
        """
        if self.stamps is not None:
            latitude = np.zeros(len(self.stamps))
            for ii, stamp in enumerate(self.stamps):
                latitude[ii] = stamp[1][0].latitude
            return np.median(latitude[np.nonzero(latitude)])
        else:
            return None
    
    @property
    def longitude(self):
        """
        median longitude value from all the GPS stamps in decimal degrees
        WGS84
        
        Only get from the GPRMC stamp as they should be duplicates
        """
        if self.stamps is not None:
            longitude = np.zeros(len(self.stamps))
            for ii, stamp in enumerate(self.stamps):
                longitude[ii] = stamp[1][0].longitude
            return np.median(longitude[np.nonzero(longitude)])
        else:
            return None
    
    @property
    def elevation(self):
        """
        median elevation value from all the GPS stamps in decimal degrees
        WGS84
        
        Only get from the GPGGA stamp as they should be duplicates
        """
        if self.stamps is not None:
            elevation = np.zeros(len(self.stamps))
            for ii, stamp in enumerate(self.stamps):
                if len(stamp[1]) == 1:
                    elev = stamp[1][0].elevation
                if len(stamp[1]) == 2:
                    elev = stamp[1][1].elevation
                if elev is None:
                    continue
                elevation[ii] = elev 
            return np.median(elevation[np.nonzero(elevation)])
        else:
            return None
    
    @property
    def start_time(self):
        """
        start time is the first good GPS time stamp
        """
        if self.stamps is not None:
            return self.data_df.index[0]
        else:
            return None
        
    def _make_index_values(self):
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
                
    def _get_gps_string_list(self, nims_string):
        """
        get the gps strings assuming that there are an even amount of data
        blocks
        """
        ### get index values of $ and gps_strings
        index_values = []
        gps_str_list = []
        for ii in range(int(len(nims_string)/self.block_size)):
            index = ii*self.block_size+3
            g_char = struct.unpack('c', 
                                   nims_string[index:index+1])[0]
            if g_char == b'$':
                index_values.append((index-3)/self.block_size)
            gps_str_list.append(g_char)
        gps_raw_stamp_list = b''.join(gps_str_list).split(b'$')
        return index_values, gps_raw_stamp_list
    
    def get_gps_list(self, nims_string):
        """
        get a list of GPS strings from the main string
        """
        ### read in GPS strings into a list to be parsed later
        index_list, gps_raw_stamp_list = self._get_gps_string_list(nims_string)
        
        gps_stamp_list = []
        ### not we are skipping the first entry, it tends to be not 
        ### complete anyway
        for index, raw_stamp in zip(index_list, gps_raw_stamp_list[1:]):
            gps_obj = GPS(raw_stamp, index)
            if gps_obj.valid:
                gps_stamp_list.append(gps_obj)
            
        return self._gps_match_double_string(gps_stamp_list)

            
    def _gps_match_double_string(self, gps_obj_list):
        """
        match GPRMC and GPGGA strings together
        """
        ### match up the GPRMC and GPGGA together
        gps_match_list = []
        for ii in range(0, len(gps_obj_list)-1, 2):
            if gps_obj_list[ii] is None:
                continue
            time_stamp = gps_obj_list[ii].time_stamp
            match_list = [gps_obj_list[ii]]
            try:
                if gps_obj_list[ii+1].time_stamp.time() == time_stamp.time():
                    match_list.append(gps_obj_list[ii+1])
            except AttributeError:
                pass
            gps_match_list.append(match_list)
        return gps_match_list
        
        
    def _get_gps_stamp_indices_from_status(self, status_array):
        """
        get the index location of the stamps
        """
        
        index_values = np.where(status_array == 0)[0]
        status_index = np.zeros_like(index_values)
        for ii in range(index_values.size):
            if index_values[ii] - index_values[ii-1] == 1:
                continue
            else:
                status_index[ii] = index_values[ii]
        status_index = status_index[np.nonzero(status_index)]
        
        return status_index
    
    def get_gps_stamps(self, status_array, gps_list):
        """
        make an array of gps stamps with index values
        """
        
        stamp_indices = self._get_gps_stamp_indices_from_status(status_array)
        gps_stamps = []
        for index in stamp_indices:
            stamp_find = False
            for stamps in gps_list:
                if stamps[0].gps_type in ['GPRMC', 'gprmc']:
                    if stamps[0].index - index == 2:
                        gps_stamps.append((index, stamps))
                        stamp_find = True
                        break
                elif stamps[0].gps_type in ['GPGGA', 'gpgga']:
                    if stamps[0].index - index == 74:
                        gps_stamps.append((index, stamps))
                        stamp_find = True
                        break
            if not stamp_find:
                logging.warning('No good GPS stamp at {0} seconds'.format(index))

        return gps_stamps
    
    def find_sequence(self, data_array, block_sequence=None):
        """
        find a sequence in a given array
        """
        if block_sequence is not None:
            self.block_sequence = block_sequence
        
        n_data = data_array.size
        n_sequence = len(self.block_sequence)
        
        slices = [np.s_[ii:n_data-n_sequence+1+ii] for ii in range(n_sequence)]
        
        sequence_search =[data_array[slices[ii]] == self.block_sequence[ii]
                          for ii in range(n_sequence)][0]
        find_index = np.where(sequence_search == True)[0]
        
        return find_index
        
    def read_nims(self, fn=None):
        """
        read nims binary file
        """
        if fn is not None:
            self.fn = fn

        ### read in header information and get the location of end of header
        self.read_header(self.fn)
        
        ### load in the entire file, its not too big, start from the 
        ### end of the header information.
        with open(self.fn, 'rb') as fid:
            fid.seek(self.data_start_seek)
            data_str = fid.read()
            
        ### read in full string as unsigned integers
        data = np.frombuffer(data_str, dtype=np.uint8)
        
        ### need to make sure that the data starts with a full block
        find_first = self.find_sequence(data[0:self.block_size*5])[0]
        data = data[find_first:]
        
        ### get GPS stamps from the binary string first
        self.gps_list = self.get_gps_list(data_str[find_first:])
        
        ### check the size of the data, should have an equal amount of blocks
        if (data.size % self.block_size) != 0:
            logging.warning('odd number of bytes {0}, not even blocks'.format(data.size)+\
                            'cutting down the data by {0}'.format(data.size % self.block_size))
            end_data = (data.size - (data.size % self.block_size))
            data = data[0:end_data]
            
        data = data.reshape((int(data.size/self.block_size), 
                             self.block_size))

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
        self.stamps = self.get_gps_stamps(self.info_array['status'],
                                          self.gps_list)
         
        ### get data
        data_array = np.zeros(data.shape[0]*self.sampling_rate,
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
            data_array[comp][:] = channel_arr.flatten()
            
        ### clean things up
        ### I guess that the E channels are opposite phase?
        for comp in ['ex', 'ey']:
            data_array[comp] *= -1
            
        self.data_df = self.align_data(data_array, self.stamps) 

    def _get_first_gps_stamp(self, stamps):
        """
        get the first GPRMC stamp
        """ 
        for stamp in stamps:
            if stamp[1][0].gps_type in ['gprmc', 'GPRMC']:
                return stamp
        return None
    
    def _get_last_gps_stamp(self, stamps):
        """
        get the last gprmc stamp
        """
        for stamp in stamps[::-1]:
            if stamp[1][0].gps_type in ['gprmc', 'GPRMC']:
                return stamp
        return None
    
    def check_timing(self, stamps):
        """
        make sure that there are the correct number of seconds in between
        the first and last GPS GPRMC stamps
        """
        timing_valid = False
        first_stamp = self._get_first_gps_stamp(stamps)[1][0]
        last_stamp = self._get_last_gps_stamp(stamps)[1][0]
        
        time_diff = last_stamp.time_stamp - first_stamp.time_stamp
        index_diff = last_stamp.index - first_stamp.index
        
        if time_diff.total_seconds() != index_diff:
            difference = time_diff.total_seconds() - index_diff
            if difference > 0:
                print('Timing might be off by {0} seconds, '.format(abs(difference))+\
                      'index of time stamps are greater than time difference.')
            else:
                print('Timing might be off by {0} seconds, '.format(abs(difference))+\
                      'time difference greater than index of time stamps.')
            return False
        else:
            timing_valid = True
            return timing_valid
                   
    def align_data(self, data_array, stamps):
        """
        Need to match up the first good GPS stamp with the data
        
        Do this by using the first GPS stamp and assuming that the time from
        the first time stamp to the start is the index value.
        
        put the data into a pandas data frame that is indexed by time
        """
        ### check timing first to make sure there is no drift
        timing_valid = self.check_timing(stamps)
        if timing_valid is False:
            print('Check time series for timing issues')
        ### first GPS stamp within the data is at a given index that is 
        ### assumed to be the number of seconds from the start of the run.
        ### therefore make the start time the first GPS stamp time minus
        ### the index value for that stamp.
        ### need to be sure that the first GPS stamp has a date, need GPRMC
        first_stamp = self._get_first_gps_stamp(stamps)
        first_index = first_stamp[0]
        start_time = first_stamp[1][0].time_stamp - \
                            datetime.timedelta(seconds=int(first_index)+1)


        dt_index = self.make_dt_index(start_time.isoformat(),
                                      self.sampling_rate,
                                      n_samples=data_array.shape[0])
        
        return pd.DataFrame(data_array, index=dt_index)
        
    def calibrate_data(self, data_df):
        """
        Apply calibrations to data
        """
        
        data_df[['hx', 'hy', 'hz']] *= self.h_conversion_factor
        data_df[['ex', 'ey']] *= self.e_conversion_factor
        data_df['ex'] /= self.ex_length/1000.
        data_df['ey'] /= self.ey_length/1000.
        
        return data_df
        
    def make_dt_index(self, start_time, sampling_rate, stop_time=None,
                      n_samples=None):
        """
        make time index array

        .. note:: date-time format should be YYYY-M-DDThh:mm:ss.ms UTC

        :param start_time: start time
        :type start_time: string

        :param end_time: end time
        :type end_time: string

        :param sampling_rate: sampling_rate in samples/second
        :type sampling_rate: float
        """

        # set the index to be UTC time
        dt_freq = '{0:.0f}N'.format(1./(sampling_rate)*1E9)
        if stop_time is not None:
            dt_index = pd.date_range(start=start_time,
                                     end=stop_time,
                                     freq=dt_freq,
                                     closed='left',
                                     tz='UTC')
        elif n_samples is not None:
            dt_index = pd.date_range(start=start_time,
                                     periods=n_samples,
                                     freq=dt_freq,
                                     tz='UTC')
        else:
            raise ValueError('Need to input either stop_time or n_samples')

        return dt_index
                   
# =============================================================================
# Exceptions
# =============================================================================
class NIMSError(Exception):
    pass
    
#### TOFO: need to align gps stamps
# =============================================================================
# Test
# =============================================================================
#
lp_dir = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\FieldWork\LP_Data"
for folder in os.listdir(lp_dir):
    nims_fn = os.path.join(lp_dir, folder, 'DATA.BIN')
    st = datetime.datetime.now()
    nims_obj = NIMS(nims_fn)
    print(nims_obj.latitude, 
          nims_obj.longitude,
          nims_obj.elevation,
          nims_obj.start_time,
          nims_obj.run_id,
          len(nims_obj.stamps))

    et = datetime.datetime.now()
    tdiff = et - st
    print('Took {0} seconds'.format(tdiff.total_seconds()))
    
#nims_fn = r"c:\Users\jpeacock\OneDrive - DOI\MountainPass\FieldWork\LP_Data\Mnp301a\DATA.BIN"
##nims_fn = r"c:\Users\jpeacock\Downloads\data_rgr022c.bnn"
#st = datetime.datetime.now()
#nims_obj = NIMS(nims_fn)
##nims_obj.read_header(nims_fn)
#
#et = datetime.datetime.now()
#
#tdiff = et - st
#print('Took {0} seconds'.format(tdiff.total_seconds()))
