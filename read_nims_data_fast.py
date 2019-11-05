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
class GPSError(Exception):
    pass

class GPS(object):
    """
    class to parse GPS stamp from the NIMS
    
    Depending on the type of Stamp there will be different attributes
    
    GPRMC has full date and time information and declination
    GPGGA has elevation data
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
                                   11:'declination_hemisphere',
                                   'length':12,
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
                                   'length':15,
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
        self.parse_gps_string()
        
    def parse_gps_string(self):
        """
        parse a gps string
        """
        if isinstance(self.gps_string, bytes):
            gps_list = self.gps_string.strip().split(b',')
            gps_list = [value.decode() for value in gps_list]
        else:
            gps_list = self.gps_string.strip().split(',')
            
        gps_list = self.validate_gps_list(gps_list)
        if gps_list is None:
            print('xxx GPS string not correct {0}'.format(self.gps_string))
            return

        attr_dict = self.type_dict[gps_list[0].lower()]
            
        for index, value in enumerate(gps_list):
            setattr(self, '_'+attr_dict[index], value)
            
    def validate_gps_list(self, gps_list):
        """
        check to make sure the gps stamp is the correct format
        """
        g_type = gps_list[0].lower()
        if 'gpg' in g_type:
            if len(g_type) > 5:
                gps_list = ['GPGGA', g_type[-6:]] + gps_list[1:]
            elif len(g_type) < 5:
                gps_list[0] = 'GPGGA'
        elif 'gpr' in g_type:
            if len(g_type) > 5:
                gps_list = ['GPRMC', g_type[-6:]] + gps_list[1:]
            elif len(g_type) < 5:
                gps_list[0] = 'GPRMC'
        
        g_type = gps_list[0].lower()
        if g_type not in ['gpgga', 'gprmc']:
            raise GPSError('GPS String type not correct.  '+\
                           'Expect GPGGA or GPRMC, got {0}'.format(g_type.upper()))
        
        self._validate_list_length(gps_list)
        self._validate_time(gps_list[self.type_dict[g_type]['time']])
        self._validate_latitude(gps_list[self.type_dict[g_type]['latitude']])
        self._validate_longitude(gps_list[self.type_dict[g_type]['longitude']])
        
        if g_type == 'gprmc':
            self._validate_date(gps_list[self.type_dict['gprmc']['date']])
            
        elif g_type == 'gpgga':
            self._validate_latitude_elevation(gps_list[self.type_dict['gpgga']['elevation']])
            
        return gps_list
    
    def _validate_list_length(self, gps_list):
        """validate gps list length based on type of string"""
        
        gps_list_type = gps_list[0].lower()
        expected_len = self.type_dict[gps_list_type]['length']
        if len(gps_list) != expected_len:
            raise GPSError('GPS string not correct length for {0}.  '.format(gps_list_type.upper())+\
                           'Expected {0}, got {1}'.format(expected_len, 
                                                          len(gps_list)))
            
    def _validate_time(self, time_str):
        """ validate time string, should be 6 characters long and an int """
        if len(time_str) != 6:
            raise GPSError('Lenght of time string {0} not correct.  '.format(time_str)+\
                           'Expected 6 got {0}'.format(len(time_str)))
        try:
            int(time_str)
        except ValueError:
            raise GPSError('Could not convert time string {0}'.format(time_str))
        
        return
    
    def _validate_date(self, date_str):
        """ validate date string, should be 6 characters long and an int """
        if len(date_str) != 6:
            raise GPSError('Lenght of date string not correct {0}.  '.format(date_str)+\
                           'Expected 6 got {0}'.format(len(date_str)))
        try:
            int(date_str)
        except ValueError:
            raise GPSError('Could not convert date string {0}'.format(date_str))
        
        return True
    
    def _validate_latitude(self, latitude_str, hemisphere_str):
        """validate latitude, should have hemisphere string with it"""
        
        if len(latitude_str) < 7:
            raise GPSError('Latitude string should be larger than 7 characters.  '+\
                           'Got {0}'.format(len(latitude_str)))
        if len(hemisphere_str) != 1:
            raise GPSError('Latitude hemispher should be 1 character.  '+\
                           'Got {0}'.format(len(hemisphere_str)))
        if hemisphere_str.lower() not in ['n', 's']:
            raise GPSError('Latitude hemisphere {0} not understood'.format(hemisphere_str.upper()))
        try:
            int(latitude_str)
        except ValueError:
            raise GPSError('Could not convert latitude string {0}'.format(latitude_str))
            
        return
    
    def _validate_longitude(self, longitude_str, hemisphere_str):
        """validate latitude, should have hemisphere string with it"""
        
        if len(longitude_str) < 7:
            raise GPSError('Longitude string should be larger than 7 characters.  '+\
                           'Got {0}'.format(len(longitude_str)))
        if len(hemisphere_str) != 1:
            raise GPSError('Longitude hemispher should be 1 character.  '+\
                           'Got {0}'.format(len(hemisphere_str)))
        if hemisphere_str.lower() not in ['e', 'w']:
            raise GPSError('Longitude hemisphere {0} not understood'.format(hemisphere_str.upper()))
        try:
            int(longitude_str)
        except ValueError:
            raise GPSError('Could not convert longitude string {0}'.format(longitude_str))
            
        return
    
    def _validate_elevation(self, elevation_str):
        """validate elevation, check for converstion to float"""
        try:
            float(elevation_str)
        except ValueError:
            raise GPSError('Elevation could not be converted {0}'.format(elevation_str))
            
            
            
    @property
    def latitude(self):
        """
        Latitude in decimal degrees, WGS84
        """
        if hasattr(self, '_latitude') and hasattr(self, '_latitude_hemisphere'):
            index = len(self._latitude) - 7
            lat = float(self._latitude[0:index]) + float(self._latitude[index:])/60
            if 's' in self._latitude_hemisphere.lower():
                lat *= -1
            return lat
        else:
            return None
        
    @property
    def longitude(self):
        """
        Latitude in decimal degrees, WGS84
        """
        if hasattr(self, '_latitude') and hasattr(self, '_latitude_hemisphere'):
            index = len(self._longitude) - 7
            lon = float(self._longitude[0:index]) + float(self._longitude[index:])/60
            if 'w' in self._longitude_hemisphere.lower():
                lon *= -1
            return lon
        else:
            return None
        
    @property
    def elevation(self):
        """
        elevation in meters
        """
        if hasattr(self, '_elevation'):
            try:
                return float(self._elevation)
            except ValueError:
                print('xxx Could not get elevation GPS string not complete ')
                print('xxx {0}'.format(self.gps_string))
        else:
            return None
        
    @property
    def time_stamp(self):
        """
        return a datetime object of the time stamp
        """
        if not hasattr(self, '_time'):
            return None
        if hasattr(self, '_date'):
            try:
                return dateutil.parser.parse('{0} {1}'.format(self._date, self._time),
                                             dayfirst=True)
            except ValueError:
                print('xxx bad date string {0}'.format(self.gps_string))
                return None
        else:
            try:
                return dateutil.parser.parse('{0} {1}'.format('010180', self._time),
                                             dayfirst=True)
            except ValueError:
                print('xxx bad time string {0}'.format(self.gps_string))
                return None
        
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
        data_start_byte = last_line[0:1]
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
        
        self.indices = self.make_index_values()
        
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
                if stamp[1][1].elevation is None:
                    continue
                elevation[ii] = stamp[1][1].elevation 
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
        
        ### replace all the non gps string bytes with nothing to sort easier
        for replace_str in [b'\xd9', b'\xc7', b'\xcc']:
            gps_str = gps_str.replace(replace_str, b'')
            
        ### sometimes the end is set with a zero for some reason
        gps_str = gps_str.replace(b'\x00', b'*')
        
        ### split the string by the $ 
        gps_str_list = gps_str.split(b'$')
        
        ### need to make sure there is an end to the gps string otherwise it
        ### might not be usefult
        g = []
        for stamp in gps_str_list:
            if stamp.find(b'*') < 0:
                print('   No end to stamp {0}'.format(stamp))
            else:
                try:
                    g.append(stamp[0:stamp.find(b'*')].decode())
                except UnicodeDecodeError:
                    print('  stamp not correct format, {0}'.format(stamp))
        gps_str_list = g
        
        ### check the first few stamps
        if gps_str_list[0].find('$') == -1:
            gps_str_list = gps_str_list[1:]
            
        self.gps_list = self.gps_match_double_string(gps_str_list)

            
    def gps_match_double_string(self, gps_string_list):
        """
        match GPRMC and GPGGA strings together
        """
        ### see if there are a GPRMC and GPGGA match in the first few stamps
        match = []
        for ii in range(1, 6):
            if len(gps_string_list[ii]) > 12 and len(gps_string_list[ii-1]) > 12:
                if gps_string_list[ii].count(',') > 10 and gps_string_list[ii-1].count(',') > 10:
                    if gps_string_list[ii].split(',')[1] == gps_string_list[ii-1].split(',')[1]:
                        match.append(True)
                    else:
                        match.append(False)
            else:
                match.append(False)
                
        ### find the location of the first pair of stamps
        try:
            first_stamp_index = np.where(np.array(match) == True)[0][0]
        ### if the stamps are bad set the index to 0 and see what happens
        except IndexError:
            first_stamp_index = 0
            
        gps_obj_list = [GPS(stamp_str) for stamp_str in gps_string_list[first_stamp_index:]]
        
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
        self.read_header()
        
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
        self.get_gps_list(data_str[find_first:])
        
        ### check the size of the data, should have an equal amount of blocks
        if (data.size % self.block_size) == 0:
            data = data.reshape((int(data.size/self.block_size), 
                                 self.block_size))
        else:
            raise NIMSError('odd number of bytes, not even blocks')
        
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
            
        self.align_data(data_array)           
            
    def align_data(self, data_array):
        """
        Need to match up the first good GPS stamp with the data
        
        Do this by using the first GPS stamp and assuming that the time from
        the first time stamp to the start is the index value.
        
        put the data into a pandas data frame that is indexed by time
        """
        
        ### first GPS stamp within the data is at a given index that is 
        ### assumed to be the number of seconds from the start of the run.
        ### therefore make the start time the first GPS stamp time minus
        ### the index value for that stamp.
        first_index = self.stamps[0][0]
        start_time = self.stamps[0][1][0].time_stamp - \
                            datetime.timedelta(seconds=int(first_index))

        dt_index = self.make_dt_index(start_time.isoformat(),
                                      self.sampling_rate,
                                      n_samples=data_array.shape[0])
        
        self.data_df = pd.DataFrame(data_array, index=dt_index)
        
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
    
#### need to align gps stamps
# =============================================================================
# Test
# =============================================================================
#
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
