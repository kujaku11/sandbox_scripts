# -*- coding: utf-8 -*-
"""
Created on Wed May 27 18:09:33 2015

@author: jpeacock-pr
"""

"""
read new zen outputs Z3d files
"""

import numpy as np
import datetime
import time
import os
import struct
import shutil
import struct
#==============================================================================
# 
#==============================================================================

class Header(object):
    """
    class for z3d header
    """
    
    def __init__(self, header_str=None):
        self.header_str = header_str
        
        self.ad_gain = None
        self.ad_rate = None
        self.alt = None
        self.attenchannelsmask = None
        self.box_number = None
        self.box_serial = None
        self.channel = None
        self.channelserial = None
        self.duty = None
        self.fpga_buildnum = None
        self.gpsweek = None
        self.lat = None
        self.logterminal = None
        self.long = None
        self.main_hex_buildnum = None
        self.numsats = None
        self.period = None
        self.tx_duty = None
        self.tx_freq = None
        self.version = None
        
        if type(self.header_str) is str:
            self.read_header()        
    
    def read_header(self):
        """
        read in the header string
        """

        header_list = self.header_str.split('\n')
        for h_str in header_list:
            if h_str.find('=') > 0:
                h_list = h_str.split('=')
                h_key = h_list[0].strip().lower()
                h_key = h_key.replace(' ', '_').replace('/', '').replace('.', '_')
                h_value = self.convert_value(h_key, h_list[1].strip())
                setattr(self, h_key, h_value)

    def convert_value(self, key_string, value_string):
        """
        convert the value to the appropriate units given the key
        """
        
        try:
            return_value = float(value_string)
        except ValueError:
            return_value = value_string
        
        if key_string.lower() == 'lat' or key_string.lower() == 'long':
            return_value = np.rad2deg(float(value_string))
            
        return return_value
            
#==============================================================================
# meta data 
#==============================================================================
class Schedule_metadata(object):
    """
    class object for metadata of Z3d file
    """
    def __init__(self, meta_string=None):
        self.meta_string = meta_string
        
        if type(self.meta_string) is str:
            self.read_meta_string()
            
    def read_meta_string(self):
        """
        read meta data string
        """
        
        meta_list = self.meta_string.split('\n')
        for m_str in meta_list:
            if m_str.find('=') > 0:
                m_list = m_str.split('=')
                m_key = m_list[0].split('.')[1].strip()
                m_key = m_key.replace('/', '')
                m_value = m_list[1].strip()
                setattr(self, m_key, m_value)

#==============================================================================
#  Meta data class    
#==============================================================================
class Metadata(object):
    """
    class for metadata from Z3d file
    """

    def __init__(self, string=None, **kwargs):
        self.f_string = string
        self.find_metadata = True
        self.board_cal = None
        self.coil_cal = None
        self.metadata_length = 512
        self.return_string = str(self.f_string)
        if self.f_string is not None:
            self.read_metadata()
            
        
    
    def read_metadata(self):
        # read in calibration and meta data
        self.find_metadata = True
        self.board_cal = []
        self.coil_cal = []
        self.count = 0
        while self.find_metadata == True:
            test_str = self.f_string[self.count*self.metadata_length:(self.count+1)*self.metadata_length]
            if test_str.lower().find('metadata record') > 0:
                self.count += 1
                test_str = test_str.strip().split('\n')[1] 
                if test_str.count('|') > 1:
                    for t_str in test_str.split('|'):
                        if t_str.find('=') == -1:
                            pass
                        else:
                            t_list = t_str.split('=')
                            t_key = t_list[0].strip().replace('.', '_')
                            t_value = t_list[1].strip()
                            setattr(self, t_key, t_value)
                elif test_str.lower().find('cal.brd') >= 0:
                    t_list = test_str.split(',')
                    t_key = t_list[0].strip().replace('.', '_')
                    setattr(self, t_key, t_list[1])
                    for t_str in t_list[2:]:
                        t_str = t_str.replace('\x00', '').replace('|', '')
                        self.board_cal.append([float(tt.strip()) 
                                           for tt in t_str.strip().split(':')])
                # some times the coil calibration does not start on its own line
                # so need to parse the line up and I'm not sure what the calibration
                # version is for so I have named it odd
                elif test_str.lower().find('cal.ant') >= 0:
                    # check to see if the coil calibration exists  
                    cal_find = True
                    if test_str.find('|') > 0:
                        odd_str = test_str.split('|')[0]
                        odd_list = odd_str.split(',')
                        odd_key = odd_list[0].strip().replace('.', '_')
                        setattr(self, odd_key, odd_list[1].strip())
                        
                        #this may be for a specific case so should test this
                        test_str = test_str.split('|')[1]
                        test_list = test_str.split(',')
                        if test_list[0].lower().find('cal.ant') >= 0:
                            m_list = test_list[0].split('=')
                            m_key = m_list[0].strip().replace('.', '_')
                            setattr(self, m_key, m_list[1].strip())
                        else:
                            for t_str in test_list[1:]:
                                self.coil_cal.append([float(tt.strip()) 
                                                 for tt in t_str.split(':')])
                elif cal_find:
                    t_list = test_str.split(',')
                    for t_str in t_list:
                        if t_str.find('\x00') >= 0:
                            pass
                        else:
                            self.coil_cal.append([float(tt.strip()) 
                                                for tt in t_str.strip().split(':')])
            else:
                self.find_metadata = False
                    
        # make coil calibration and board calibration structured arrays
        if len(self.coil_cal) > 0:
            self.coil_cal = np.core.records.fromrecords(self.coil_cal, 
                                           names='frequency, amplitude, phase',
                                           formats='f8, f8, f8') 
        if len(self.board_cal) > 0:
            self.board_cal = np.core.records.fromrecords(self.board_cal, 
                                   names='frequency, rate, amplitude, phase',
                                   formats='f8, f8, f8, f8')
        self.return_string = self.f_string[self.count*self.metadata_length:]
#==============================================================================
# 
#==============================================================================
fn = r"d:\Peacock\MTData\Test\mb666\mb666_20150527_204016_256_HX.Z3D"
file_size = os.path.getsize(fn)
fid = file(fn, 'rb')
#f_str = fid.read()
st = time.time()

gps_flag_0 = np.int32(2147483647)
gps_flag_1 = np.int32(-2147483648)
gps_f0 = gps_flag_0.tostring()
gps_f1 = gps_flag_1.tostring()
gps_flag = gps_f0+gps_f1

gps_stamp_length = 64
gps_bytes = gps_stamp_length/4    
               
gps_dtype = np.dtype([('flag0', np.int32),
                      ('flag1', np.int32),
                      ('time', np.int32),
                      ('lat', np.float64),
                      ('lon', np.float64),
                      ('num_sat', np.int32),
                      ('gps_sens', np.int32),
                      ('temperature', np.float32),
                      ('voltage', np.float32),
                      ('num_fpga', np.int32),
                      ('num_adc', np.int32),
                      ('pps_count', np.int32),
                      ('dac_tune', np.int32),
                      ('block_len', np.int32)])


header_length = 512

# read in header
header_string = fid.read(header_length)
#header_string = f_str[0:header_length]
header = Header(header_string)

# read in schedule info
meta_data_string = fid.read(header_length)
#meta_data_string = f_str[header_length:2*header_length]
meta_schedule = Schedule_metadata(meta_data_string)

# read in metadata and calibrations

metadata_string = fid.read(17*header_length)

metadata = Metadata(metadata_string)

data = np.zeros((file_size-512*(2+metadata.count))/4, dtype=np.int32)
test_str = np.fromstring(metadata.return_string, dtype=np.int32)
data[0:len(test_str)] = test_str
data_count = len(test_str)
#==============================================================================
# 
#==============================================================================
block_len = 2**16
while data_count < data.size:
    
    test_str = np.fromstring(fid.read(block_len), dtype=np.int32)
    data[data_count:data_count+len(test_str)] = test_str
    data_count += test_str.size
    
fid.close()
# find the gps stamps
gps_stamp_find = np.where(data==gps_flag_0)[0]
# skip the first two stamps and trim data
data = data[gps_stamp_find[3]:]
gps_stamp_find = np.where(data==gps_flag_0)[0]

gps_stamps = np.zeros(len(gps_stamp_find), dtype=gps_dtype)

for ii, gps_find in enumerate(gps_stamp_find):
    if data[gps_find+1] == gps_flag_1:
        gps_str = struct.pack('<'+'i'*gps_bytes, *data[gps_find:gps_find+gps_bytes])
        gps_stamps[ii] = np.fromstring(gps_str, dtype=gps_dtype)
        if ii > 0:
            gps_stamps[ii]['block_len'] = gps_find-gps_stamp_find[ii-1]-gps_bytes 
        elif ii == 0:
            gps_stamps[ii]['block_len'] = 0
        data[gps_find:gps_find+gps_bytes] = 0

# trim the data after taking out the gps stamps
time_series = data[np.nonzero(data)]
    
# need to check


### read in the time series
#block_len = int(header.ad_rate*4+gps_stamp_length)
#max_ts_size = (file_size-512*(2+metadata.count))/4
#max_gps_stamps = int(np.ceil(max_ts_size/(header.ad_rate)))
#gps_stamps = np.zeros(max_gps_stamps, dtype=gps_dtype)
#ts2 = np.zeros(max_ts_size, np.int32)
#
#stamp_find = test_str.find(gps_flag)
#ts_count = 0
#if stamp_find >= 0:
#    try:
#        stamp_str = test_str[stamp_find:gps_stamp_length]
#    except IndexError:
#        stamp_str += fid.read(gps_stamp_length-len(test_str[stamp_find:]))
#    
#    gps_stamp = np.fromstring(stamp_str, dtype=gps_dtype)
#    gps_stamps[0] = gps_stamp
#    test_str = test_str[stamp_find+gps_stamp_length:]
#    stamp_find = test_str.find(gps_stamp)
#    gps_count = 1
#    if stamp_find >= 0:
#        ts_0 = np.fromstring(test_str[0:stamp_find+1], np.int32)
#        ts2[0:ts_0.size] = ts_0
#        ts_count = ts_0.size
#        gps_stamp = np.fromstring(stamp_str[stamp_find:stamp_find+gps_stamp_length],
#                                  dtype=gps_dtype)
#        gps_stamps[1] = gps_stamp
#        gps_count += 1
#        ts_0 = np.fromstring(test_str[stamp_find+gps_stamp_length:], np.int32)
#        ts2[ts_count:ts_count+ts_0.size] = ts_0
#        ts_count += ts_0.size
#    else:
#        ts_0 = np.fromstring(test_str, np.int32)
#        ts2[0:ts_0.size] = ts_0
#        ts_count = ts_0.size
#        
#    
#elif stamp_find == -1:
#    stamp_find = False
#    # find first time stamp
#    stamp_find = False
#    while stamp_find == False:
#        test_str = fid.read(4)
#        if test_str == gps_f0:
#            test_flag_2 = fid.read(4)
#            if test_flag_2 == gps_f1:
#                gps_stamp_str = test_str+test_flag_2+fid.read(gps_stamp_length-8)
#                gps_stamp = np.fromstring(gps_stamp_str, dtype=gps_dtype)
#                gps_stamps[0] = gps_stamp
#                stamp_find = True
#    ts_count = 0
#    gps_count = 1
#    
#
#
#
#gps_count = 1
#block_count = 0
#while test_str != '' or gps_count > max_gps_stamps:
#    test_str = fid.read(4)
#    if test_str == gps_flag_0.tostring():
#        test_flag_2 = fid.read(4)
#        if test_flag_2 == gps_flag_1.tostring():
#            gps_stamp_str = test_str+test_flag_2+fid.read(gps_stamp_length-8)
#            gps_stamp = np.fromstring(gps_stamp_str, dtype=gps_dtype)
#            gps_stamps[gps_count] = gps_stamp
#            gps_count += 1
#            block_count = 0
#    else:
#        if test_str == '':
#            break
#        ts2[ts_count] = np.fromstring(test_str, dtype=np.int32)
#        ts_count += 1
#        block_count += 1

et = time.time()
print 'started at: {0}'.format(st)
print 'ended at  : {0}'.format(et)
print '--> took: {0:.3f}'.format(et-st)