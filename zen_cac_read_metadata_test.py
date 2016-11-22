# -*- coding: utf-8 -*-
"""
Created on Fri May 29 15:50:56 2015

@author: jpeacock-pr
"""
import numpy as np


cfn = r"d:\Peacock\MTData\Test\mb666\Merged\mt0_20150527_204008_256.cac"
#line_str_find = -1
#header_dict = {}
#file_pointer_size = 10
#
#flag_dtype = [('length', np.int32),
#              ('flag', np.int32),
#              ('type', np.int16)]
#              
#flag_len = 10
#len_bytes = 4

class Cache_Metadata(object):
    def __init__(self, fn=None, **kwargs):
        self.fn = fn
        self.ch_adcardsn = None
        self.ch_azimuth = None
        self.ch_cmp = None
        self.ch_cres = None
        self.ch_factor = None
        self.ch_gain = None
        self.ch_gainfactor = None
        self.ch_gdpslot = None
        self.ch_length = None
        self.ch_lowpass = None
        self.ch_number = None
        self.ch_numon = None
        self.data_version = None
        self.gdp_cardtype = None
        self.gdp_date = None
        self.gdp_operator = None
        self.gdp_progver = None
        self.gdp_time = None
        self.gdp_type = None
        self.gps_alt = None
        self.gps_lat = None
        self.gps_lon = None
        self.gps_numsat = None
        self.gps_sec = None
        self.gps_utmzone = None
        self.gps_week = None
        self.header_type = None
        self.job_by = None
        self.job_for = None
        self.job_name = None 
        self.job_number = None
        self.line_name = None
        self.rx_aspace = None
        self.rx_sspace = None
        self.rx_utm0 = None
        self.rx_utm1 = None
        self.rx_utm2 = None
        self.rx_xyz0 = None
        self.rx_xyz1 = None
        self.rx_xyz2 = None
        self.survey_acqmethod = None
        self.survey_type = None
        self.ts_adfreq = None
        self.ts_npnt = None
        self.unit_length = None
        

        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            
    def read_meta_string(self, meta_string=None):
        """
        read in a meta from the raw string
        """
        
        if meta_string is not None:
            self._meta_string = meta_string
            
            meta_list = self._meta_string.split('\n')
            for m_str in meta_list:
                line_list = m_str.strip().split(',')
                l_key = line_list[0].replace('.', '_').lower()
                l_value = line_list[1:]
                if len(l_value) == 1:
                    try:
                        l_value = float(l_value[0])
                    except ValueError:
                        l_value = l_value[0]
                setattr(self, l_key, l_value)
                
class Board_Calibration(object):
    """
    deal with baord calibration 
    """
    
    def __init__(self, board_cal_str=None, **kwargs):
        self.board_cal_str = board_cal_str
        
        self.cal_sys = {}
        self.cal_ant = {}
        
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            
    def read_board_cal_str(self, board_cal_str=None):
        """
        read board calibration data
        """
        
        if board_cal_str is not None:
            self.board_cal_str = board_cal_str
            
            
        cal_list = self.board_cal_str.split('\n')
        for c_str in cal_list:
            c_list = c_str.split(',')
            c_key = c_list[0].replace('.', '_').lower()
            if len(c_list) == 2:
               c_value = c_list[1]
               setattr(self, c_key, c_value)
            elif len(c_list) > 2:
                c_key2 = c_list[1]
                c_arr = np.zeros(len(c_list[2:]), 
                                 dtype=[('frequency', np.float),
                                        ('amplitude', np.float),
                                        ('phase', np.float)])
                for ii, cc in enumerate(c_list[2:]):
                    c_arr[ii] = np.array([float(kk) for kk in cc.split(':')])
        
                self.__dict__[c_key][c_key2] = c_arr
                
class Cache(object):
    """
    deal with Zonge .cac files
    """
    def __init__(self, fn=None, **kwargs):
        self.fn = fn
        
        self.metadata = None
        self.time_series = None
        self.other = None
        self.calibration = None
        
        self._flag_len = 10
        self._len_bytes = 4
        self._flag_dtype = [('length', np.int32),
                            ('flag', np.int32),
                            ('type', np.int16)]
              

        self._type_dict = {4:'navigation',
                           514:'metadata',
                           768:'calibration',
                           16:'time_series',
                           15:'other',
                           640:'status'}
                           
        self._f_tell = 0
                
    def _read_file_block(self, file_id):
        """
        read a cache block
        """
        file_pointer = np.fromstring(file_id.read(self._flag_len),
                                     dtype=self._flag_dtype)
        f_str = file_id.read(file_pointer['length']-2)
        end_len = np.fromstring(file_id.read(self._len_bytes),
                                dtype=np.int32)
        
        if self._validate_block_len(file_pointer, end_len) is True:
            self._f_tell = file_id.tell()
            return file_pointer, f_str
        
    def _validate_block_len(self, file_pointer, end_length):
        """
        validate that the block lengths as defined at the beginning and 
        the end are the same
        """
        
        try:
            assert file_pointer['length'] == end_length
            return True
        except AssertionError:
            raise ValueError('File pointer length {0} != end length {1}'.format(
                             file_pointer['length'], end_length))
                             
    def read_cache_metadata(self, fn=None):
        """
        read .cac file
        """
        if fn is not None:
            self.fn = fn
        
        f_pointer = True
        with open(self.fn, 'rb') as fid:
            while f_pointer:            
                # read in first pointer            
                f_pointer, f_str = self._read_file_block(fid)
                
                # if the data type is the meta data
                if int(f_pointer['type']) == 514:
                    meta_obj = Cache_Metadata()
                    meta_obj.read_meta_string(f_str)

                    key = self._type_dict[int(f_pointer['type'])]        
                    setattr(self, key, meta_obj)
                    print 'Read in metadata'
                    return
                            
        
    def read_cache_file(self, fn=None):
        """
        read .cac file
        """
        if fn is not None:
            self.fn = fn
        
        f_pointer = True
        with open(self.fn, 'rb') as fid:
            while f_pointer:            
                # read in first pointer            
                f_pointer, f_str = self._read_file_block(fid)
                
                # if the data type is the meta data
                if int(f_pointer['type']) == 514:
                    meta_obj = Cache_Metadata()
                    meta_obj.read_meta_string(f_str)

                    key = self._type_dict[int(f_pointer['type'])]        
                    setattr(self, key, meta_obj)
                    print 'Read in metadata'
                    continue
                
                # if the data type is calibration
                elif int(f_pointer['type']) == 768:
                    cal_obj = Board_Calibration(f_str)
                    cal_obj.read_board_cal_str()
                    
                    key = self._type_dict[int(f_pointer['type'])]        
                    setattr(self, key, cal_obj)
                    print 'Read in calibration'
                    continue
                    
                # if the data type is time series
                elif int(f_pointer['type']) == 16:
                    ts_arr = np.fromstring(f_str, dtype=np.int32)
                    ts_arr = np.resize(ts_arr, (int(self.metadata.ts_npnt), 
                                                len(self.metadata.ch_cmp)))
                    
                    
                    ts = np.zeros(1, 
                                  dtype=[(cc.lower(), np.int32, 
                                          (int(self.metadata.ts_npnt),)) for 
                                          cc in self.metadata.ch_cmp])
                    
                    for ii, cc in enumerate(self.metadata.ch_cmp):
                        ts[cc.lower()][:] = ts_arr[:, ii]
                    key = self._type_dict[int(f_pointer['type'])]        
                    setattr(self, key, ts)
                    print 'Read in time series,  # points = {0}'.format(
                                                        self.metadata.ts_npnt)
                    return
                # if the data type is time series
                elif int(f_pointer['type']) == 15:
                    ts = np.fromstring(f_str, dtype=np.int32)
                    

                
                    key = self._type_dict[int(f_pointer['type'])]        
                    setattr(self, key, ts)
                    print 'Read in other'
                    continue
                
    
#==============================================================================
#  test    
#==============================================================================
cac = Cache(cfn)
cac.read_cache_file()


## the format of the .cac file is <length><flag><data_type><data><length>
#with open(cfn, 'rb') as fid:
#    # need to skip the file pointer pointer
#
#    f_dict, f_tell = read_block(fid)
    
#    h_flag = np.fromstring(fid.read(flag_len), dtype=flag_dtype)
#    meta_str = fid.read(h_flag['length']-2)
#    meta_obj = Cache_Metadata()
#    meta_obj.read_meta_string(meta_str)
#    end_h_flag = np.fromstring(fid.read(len_bytes), dtype=np.int32)
#    cal_flag = np.fromstring(fid.read(flag_len), dtype=flag_dtype)
#    cal_str = fid.read(cal_flag['length']-2)
#    board_cal_obj = Board_Calibration(cal_str)
#    board_cal_obj.read_board_cal_str()
#    end_cal_flag = np.fromstring(fid.read(len_bytes), dtype=np.int32)
#    ts_flag = np.fromstring(fid.read(flag_len), dtype=flag_dtype)
    

#cm = Cache_Metadata()
#cm.read_meta_string(meta_str)       
    