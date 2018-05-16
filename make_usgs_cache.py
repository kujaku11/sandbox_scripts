# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 16:38:28 2017

@author: jpeacock
"""
#==============================================================================

import os
import struct
import shutil
import time
import datetime
from collections import Counter

import numpy as np
import scipy.signal as sps
import pandas as pd

import mtpy.usgs.zen as zen
import mtpy.utils.filehandling as mtfh
import mtpy.utils.gis_tools as gis_tools
#==============================================================================
# Cache files
#==============================================================================
class UTC(datetime.tzinfo):
    def utcoffset(self, df):
        return datetime.timedelta(hours=0)
    def dst(self, df):
        return datetime.timedelta(0)
    def tzname(self, df):
        return "UTC"

class Metadata(object):
    def __init__(self, fn=None, **kwargs):
        self.fn = fn
        self.SurveyID = None
        self.SiteID = None
        self.RunID = None
        self._latitude = None
        self._longitude = None
        self._elevation = None
        self._start_time = None
        self._stop_time = None
        self._sampling_rate = None
        self._n_samples = None
        self.channel_dict = None
        self.MissingDataFlag = 1e9
        self._chn_num = None
        self.CoordinateSystem = None
        self._time_fmt = '%Y-%m-%dT%H:%M:%S %Z'
        self._metadata_len = 30
        
        self._key_list = ['SurveyID',
                          'SiteID',
                          'RunID',
                          'SiteLatitude',
                          'SiteLongitude',
                          'SiteElevation',
                          'AcqStartTime',
                          'AcqStopTime',
                          'AcqSmpFreq',
                          'AcqNumSmp',
                          'Nchan',
                          'CoordinateSystem',
                          'ChnSettings',
                          'MissingDataFlag',
                          'DataSet']
        
        self._chn_settings = ['ChnNum',
                              'ChnID',
                              'InstrumentID',
                              'Azimuth',
                              'Dipole_Length']
        self._chn_fmt = {'ChnNum':'<7',
                         'ChnID':'<6',
                         'InstrumentID':'<13',
                         'Azimuth':'>7.1f',
                         'Dipole_Length':'>14.1f'}

        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            
            
    @property
    def SiteLatitude(self):
        return gis_tools.convert_position_float2str(self._latitude)
    
    @SiteLatitude.setter
    def SiteLatitude(self, lat):
        self._latitude = gis_tools.assert_lat_value(lat)
        
    @property
    def SiteLongitude(self):
        return gis_tools.convert_position_float2str(self._longitude)
    
    @SiteLongitude.setter
    def SiteLongitude(self, lon):
        self._longitude = gis_tools.assert_lon_value(lon)
        
    @property
    def SiteElevation(self):
        return self._elevation
    
    @SiteElevation.setter
    def SiteElevation(self, elev):
        self._elevation = gis_tools.assert_elevation_value(elev)
        
    @property
    def AcqStartTime(self):
        return self._start_time.strftime(self._time_fmt)
    
    @AcqStartTime.setter
    def AcqStartTime(self, time_string):
        dt = datetime.datetime.strptime(time_string, self._time_fmt)
        self._start_time = datetime.datetime(dt.year, dt.month, dt.day,
                                             dt.hour, dt.minute, dt.second,
                                             dt.microsecond, tzinfo=UTC())
        
    @property
    def AcqStopTime(self):
        return self._stop_time.strftime(self._time_fmt)
    
    @AcqStopTime.setter
    def AcqStopTime(self, time_string):
        dt = datetime.datetime.strptime(time_string, self._time_fmt)
        self._stop_time = datetime.datetime(dt.year, dt.month, dt.day,
                                            dt.hour, dt.minute, dt.second,
                                            dt.microsecond, tzinfo=UTC())
    
    @property
    def Nchan(self):
        return self._chn_num
    
    @Nchan.setter
    def Nchan(self, n_channel):
        try:
            self._chn_num = int(n_channel)
        except ValueError:
            print("{0} is not a number, setting Nchan to 0".format(n_channel))
            
    @property
    def AcqSmpFreq(self):
        return self._sampling_rate
    @AcqSmpFreq.setter
    def AcqSmpFreq(self, df):
        self._sampling_rate = float(df)

    @property
    def AcqNumSmp(self):
        return self._n_samples

    @AcqNumSmp.setter
    def AcqNumSmp(self, n_samples):
        self._n_samples = int(n_samples)            

    def read_metadata(self, meta_lines=None):
        """
        read in a meta from the raw string
        """
        chn_find = False
        comp = 0
        self.channel_dict = {}
        if meta_lines is None:
            with open(self.fn, 'r') as fid:
                meta_lines = [fid.readline() for ii in range(self._metadata_len)]
        for ii, line in enumerate(meta_lines):
            if line.find(':') > 0:
                key, value = line.strip().split(':', 1)
                value = value.strip()
                if len(value) < 1 and key == 'DataSet':
                    chn_find = False
                    # return the line that the data starts on that way can
                    # read in as a numpy object or pandas
                    return ii+1
                elif len(value) < 1:
                    chn_find = True
                setattr(self, key, value)
            elif 'coordinate' in line:
                self.CoordinateSystem = ' '.join(line.strip().split()[-2:])
            else:
                if chn_find is True:
                    if 'chnnum' in line.lower():
                        ch_key = line.strip().split()
                    else:
                        line_list = line.strip().split()
                        if len(line_list) == 5:
                            comp += 1
                            self.channel_dict[comp] = {}
                            for key, value in zip(ch_key, line_list):
                                if key.lower() in ['azimuth', 'dipole_length']:
                                    value = float(value)
                                self.channel_dict[comp][key] = value
                        else:
                            print('Not sure what line this is')
                            
    def write_metadata(self):
        """
        Write out metadata in the format of PB
        
        returns a list of lines to write use '\n'.join(lines) to write out
        """
        lines = []
        for key in self._key_list:
            if key in ['ChnSettings']:
                lines.append('{0}:'.format(key))
                lines.append(' '.join(self._chn_settings))
                for chn_key in sorted(self.channel_dict.keys()):
                    chn_line = []
                    for comp_key in self._chn_settings:
                        chn_line.append('{0:{1}}'.format(self.channel_dict[chn_key][comp_key],
                                        self._chn_fmt[comp_key]))
                    lines.append(''.join(chn_line))
            elif key in ['DataSet']:
                lines.append('{0}:'.format(key))
                return lines
            else:
                lines.append('{0}: {1}'.format(key, getattr(self, key)))


# =============================================================================
# Class for the asc file
# =============================================================================
class USGSasc(Metadata):
    """
    read and write Paul's ascii formatted time series
    """
    
    def __init__(self, **kwargs):
        Metadata.__init__(self)
        self.ts = None
        self.fn = None
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])
            
    def read_asc_file(self, fn=None):
        if fn is not None:
            self.fn = fn
            
        data_line = self.read_metadata()
        self.ts = pd.read_csv(self.fn,
                              delim_whitespace=True,
                              skiprows=data_line,
                              dtype=np.float32)
        
    def write_asc_file(self, save_fn, chunk_size=1024):
        str_fmt = lambda x: '{0:>11.7g}'.format(x)
        meta_lines = self.write_metadata()
        with open(save_fn, 'w') as fid:
            h_line = [''.join(['{0:>11}'.format(c.upper()) for c in self.ts.columns])]
            fid.write('\n'.join(meta_lines+h_line))
            for chunk in range(int(self.ts.shape[0]/chunk_size)):
    
                out = np.array(self.ts[chunk*chunk_size:(chunk+1)*chunk_size])
                lines = ['']
                for ii in range(chunk_size):
                    lines.append(''.join([str_fmt(num) for num in out[ii, :]]))
                fid.write('\n'.join(lines))
#            self.ts.to_csv(save_fn, 
#                           sep=' ', 
#                           float_format='%10.7g', 
#                           index=False,
#                           doublequote=False,
#                           quoting=3,
#                           escapechar=' ',
#                           chunksize=1024)
            
        
class ZenCache(object):
    """
    deals with cache files or combined time series files.
    
    This will combine all coincident files into a .cac file for use in the
    Zonge processing software.  It will start at the first coherent time
    stamp and go to the longest coherent time stamp, such that each channel 
    will have the same start time and end time and same number of data points.
    
    ================== ========================================================
     Attributes         Description
    ================== ======================================================== 
    cal_data            list of calibrations, as is from file
    fn_list              list of filenames merged together
    log_lines           list of information to put into a log file
    meta_data           dictionary of meta data key words and values
    nav_data            list of navigation data, as is from file
    save_fn             file to save merged file to
    ts                  np.ndarray(len(ts), num_channels) of time series
    verbose             [ True | False ] True prints information to console
    zt_list              list of class: Zen3D objects
    _ch_factor          scaling factor for the channels, got this from Zonge
    _ch_gain            gain on channel, not sure of the format
    _ch_lowpass_dict    dictionary of values for lowpass filter, not sure how
                        they get the values
    _data_type          np.dtype of data type for cache block
    _flag               flag for new data block
    _nav_len            length of navigation information in bytes
    _stamp_len          length of new block stamp in bytes
    _type_dict          dictionary of cache block types, from Zonge.
    ================== ========================================================
    
    Methods:
    ---------
        * *check_sampling_rate* : makes sure sampling rate is the same for all
                                  files being merged.
        
        * *check_time_series* : makes sure all time series start at the same
                                time and have the same length.
                                
        * *write_cache_file* : writes a cache file for given filenames.
        
        * *read_cache* : reads in a cache file.
        
    :Example: ::
    
        >>> import ZenTools as zen
        >>> zc = zen.ZenCache()
        >>> # read a cache file
        >>> zc.read_cache(fn=r"/home/MT/mt01_20130601_190001_4096.cac")
        >>> # write a cache file
        >>> import os
        >>> file_path = r"/home/MT/Station1"
        >>> fn_list = [os.path.join(file_path, fn) 
        >>> ...       for fn in os.listdir(file_path)
        >>> ...       if fn.find('.Z3D')>0]
        >>> zc.write_cache_file(fn_list, r"/home/MT/Station1", station='s1')
        >>> Saved File to: /home/MT/Station1/Merged/s1_20130601_190001_4096.cac
        
    """   
    
    def __init__(self):
        
        self.fn_list = None
        self.zt_list = None
        self.save_fn = None
        self._ch_factor = '9.5367431640625e-10'
        self._ch_gain = '01-0'
        self._ch_lowpass_dict = {'256':'112', 
                                 '1024':'576',
                                 '4096':'1792'}
        self._flag = -1
        self._ts_dtype = np.int32
        
        self._type_dict = {'nav' : 4,
                          'meta' :  514,
                          'cal' : 768,
                          'ts' : 16}
                          
        self._data_type = np.dtype([('len',np.int32), 
                                    ('flag', np.int32), 
                                    ('input_type', np.int16)])
        self._stamp_len = 10
        self._nav_len = 43
        
        self.nav_data = None
        self.cal_data = None
        self.ts = None
        self.verbose = True
        self.log_lines = []
        self.chn_order = ['hx','hy','hz','ex','ey']
        
        self.meta_data = {'SURVEY.ACQMETHOD' : ',timeseries',
                           'SURVEY.TYPE' : ',',
                           'LENGTH.UNITS' : ',m',
                           'DATA.DATE0' : '',
                           'DATA.TIME0' : '',
                           'TS.ADFREQ' : '',
                           'TS.NPNT': '',              
                           'CH.NUNOM' : ',',
                           'CH.FACTOR' : '',
                           'CH.GAIN' : '',
                           'CH.NUMBER' : '',
                           'CH.CMP' : '',
                           'CH.LENGTH' : '',
                           'CH.EXTGAIN' : '',
                           'CH.NOTCH' : '',
                           'CH.HIGHPASS' : '',
                           'CH.LOWPASS' : '',
                           'CH.ADCARDSN' : '',
                           'CH.STATUS' : ',',
                           'CH.SP' : ',',
                           'CH.GDPSLOT' : ',',
                           'RX.STN' : '',
                           'RX.AZIMUTH' : ',',
                           'LINE.NAME' : ',',
                           'LINE.NUMBER' : ',',
                           'LINE.DIRECTION' : ',',
                           'LINE.SPREAD' : ',',
                           'JOB.NAME' : ',',
                           'JOB.FOR' : ',',
                           'JOB.BY' : ',',
                           'JOB.NUMBER' : ',',
                           'GDP.File' : ',',
                           'GDP.SN' : ',',
                           'GDP.TCARDSN' : ',',
                           'GDP.NUMCARD' : ',',
                           'GDP.ADCARDSN' : ',',
                           'GDP.ADCARDSND' : ',',
                           'GDP.CARDTYPE' : ',',
                           'GDP.BAT' : ',',
                           'GDP.TEMP' : ',',
                           'GDP.HUMID' : ',',
                           'TS.NCYCLE' : ',',
                           'TS.NWAVEFORM' : ',',
                           'TS.DECFAC' : ',',
                           'TX.SN,NONE' : ',',
                           'TX.STN' : ',',
                           'TX.FREQ' : ',',
                           'TX.DUTY' : ',',
                           'TX.AMP' : ',',
                           'TX.SHUNT' : ','}
    
    #==================================================
    def check_sampling_rate(self, zt_list):
        """
        check to make sure the sampling rate is the same for all channels
        
        Arguments:
        -----------
            **zt_list** : list of Zen3D instances
        
        Outputs:
        --------
            **None** : raises an error if sampling rates are not all the same
            
        """
        
        nz = len(zt_list)
        
        df_list = np.zeros(nz)
        for ii, zt in enumerate(zt_list):
            df_list[ii] = zt.df
            
        tf_array = np.zeros((nz, nz))
        
        for jj in range(nz):
            tf_array[jj] = np.in1d(df_list, [df_list[jj]])
        
        false_test = np.where(tf_array==False)
        
        if len(false_test[0]) != 0:
            raise IOError('Sampling rates are not the same for all channels '+\
                          'Check file(s)'+zt_list[false_test[0]])
        
    #==================================================
    def check_time_series(self, zt_list, decimate=1):
        """
        check to make sure timeseries line up with eachother.
        
        """
        
        n_fn = len(zt_list)
        
        t_arr = np.zeros(n_fn, 
                 dtype=[('comp', 'S3'),
                        ('start', np.int64),
                        ('stop', np.int64)])
                        
        ts_list = []
        print '-'*50
        for ii, z3d_obj in enumerate(zt_list):
            dt_index = z3d_obj.ts_obj.ts.data.index.astype(np.int64)
            t_arr[ii]['comp'] = z3d_obj.metadata.ch_cmp.lower()
            t_arr[ii]['start'] = dt_index[0]
            t_arr[ii]['stop'] = dt_index[-1]
            ts_list.append(z3d_obj.ts_obj)
            if self.verbose:
                print '{0} -- {1:<16.2f}{2:<16.2f} sec'.format(z3d_obj.metadata.ch_cmp,
                                                           dt_index[0]/10.**9,
                                                           dt_index[-1]/10.**9)                 

            self.log_lines.append('{0} -- {1:<16.2f}{2:<16.2f} sec'.format(z3d_obj.metadata.ch_cmp,
                                                           dt_index[0]/10.**9,
                                                           dt_index[-1]/10.**9))
        
        # get the start and stop times that correlates with all time series
        start = t_arr['start'].max()/10**9
        stop = t_arr['stop'].min()/10**9
        
        # figure out the max length of the array, getting the time difference into
        # seconds and then multiplying by the sampling rate
        ts_len = int((stop-start)*z3d_obj.df)
        
        if decimate > 1:
            ts_len /= decimate
        
        ts_db = pd.DataFrame(np.zeros((ts_len, n_fn)), list(t_arr['comp']))
        for ii, ts in enumerate(ts_list):
            dt_index = ts.ts.data.index.astype(np.int64)/10**9
            index_0 = np.where(dt_index == start)[0][0]
            index_1 = np.where(dt_index == stop)[0][0]
            t_diff = ts_len-(index_1-index_0)
            ts.ts.data.astype(np.int32)
            if t_diff != 0:
                if self.verbose:
                    print '{0} off by {1} points --> {2} sec'.format(ts.fn,
                                                                     t_diff,
                                                                     t_diff/ts.sampling_rate)
                self.log_lines.append('{0} off by {1} points --> {2} sec \n'.format(ts.fn,
                                                                     t_diff,
                                                                     t_diff/ts.sampling_rate))
            if decimate > 1:
                 ts_db[:, ii] = sps.resample(ts.ts.data[index_0:index_1],
                                              ts_len, 
                                              window='hanning')

            else:
                ts_db[0:ts_len-t_diff, ii] = ts.ts.data[index_0:index_1]

        return ts_db, ts_len, None 
    
    #==================================================    
    def write_cache_file(self, fn_list, save_fn, station='ZEN', decimate=1):
        """
        write a cache file from given filenames
        
        """
        #sort the files so they are in order
        fn_sort_list = []
        for cs in self.chn_order:
            for fn in fn_list:
                if cs in fn.lower():
                    fn_sort_list.append(fn)

        fn_list = fn_sort_list
        print '-'*15+' Merging '+'-'*15
        for fn in fn_list:
            print fn
            
        n_fn = len(fn_list)
        self.zt_list = []
        for fn in fn_list:
            zt1 = zen.Zen3D(fn=fn)
            zt1.verbose = self.verbose
            try:
                zt1.read_z3d(convert_to_mv=False)
            except ZenGPSError:
                zt1._seconds_diff = 59
                zt1.read_z3d(convert_to_mv=False)
            self.zt_list.append(zt1)
        
            #fill in meta data from the time series file
            self.meta_data['DATA.DATE0'] = ','+zt1.schedule.Date
            self.meta_data['DATA.TIME0'] = ','+zt1.schedule.Time
            self.meta_data['TS.ADFREQ'] = ',{0}'.format(int(zt1.df))
            self.meta_data['CH.FACTOR'] += ','+self._ch_factor 
            self.meta_data['CH.GAIN'] += ','+self._ch_gain
            self.meta_data['CH.CMP'] += ','+zt1.metadata.ch_cmp.upper()
            self.meta_data['CH.LENGTH'] += ','+zt1.metadata.ch_length
            self.meta_data['CH.EXTGAIN'] += ',1'
            self.meta_data['CH.NOTCH'] += ',NONE'
            self.meta_data['CH.HIGHPASS'] += ',NONE'
            self.meta_data['CH.LOWPASS'] += ','+\
                                       self._ch_lowpass_dict[str(int(zt1.df))]
            self.meta_data['CH.ADCARDSN'] += ','+zt1.header.channelserial
            self.meta_data['CH.NUMBER'] += ',{0}'.format(zt1.metadata.ch_number)
            self.meta_data['RX.STN'] += ','+zt1.station
            
        #make sure all files have the same sampling rate
        self.check_sampling_rate(self.zt_list)
        
        #make sure the length of time series is the same for all channels
        self.ts, ts_len, temp_fn = self.check_time_series(self.zt_list,
                                                          decimate=decimate)
        
        self.meta_data['TS.NPNT'] = ',{0}'.format(ts_len)
        
        #get the file name to save to 
        if save_fn[-4:] == '.cac':
            self.save_fn = save_fn
        elif save_fn[-4] == '.':
            raise ZenInputFileError('File extension needs to be .cac, not'+\
                                    save_fn[-4:])
        else:
            general_fn = station+'_'+\
                         self.meta_data['DATA.DATE0'][1:].replace('-','')+\
                         '_'+self.meta_data['DATA.TIME0'][1:].replace(':','')+\
                         '_'+self.meta_data['TS.ADFREQ'][1:]+'.cac'
            
            if os.path.basename(save_fn) != 'Merged':             
                save_fn = os.path.join(save_fn, 'Merged')
                if not os.path.exists(save_fn):
                    os.mkdir(save_fn)
            self.save_fn = os.path.join(save_fn, general_fn)
                
                
            
        cfid = file(self.save_fn, 'wb+')
        #--> write navigation records first        
        cfid.write(struct.pack('<i', self._nav_len))
        cfid.write(struct.pack('<i', self._flag))
        cfid.write(struct.pack('<h', self._type_dict['nav']))
        for nd in range(self._nav_len-2):
            cfid.write(struct.pack('<b', 0))
        cfid.write(struct.pack('<i', self._nav_len))
        
        #--> write meta data
        meta_str = ''.join([key+self.meta_data[key]+'\n' 
                             for key in np.sort(self.meta_data.keys())])
        
        meta_len = len(meta_str)
        
        cfid.write(struct.pack('<i', meta_len+2))
        cfid.write(struct.pack('<i', self._flag))
        cfid.write(struct.pack('<h', self._type_dict['meta']))
        cfid.write(meta_str)
        cfid.write(struct.pack('<i', meta_len+2))
        
        #--> write calibrations
        cal_data1 = 'HEADER.TYPE,Calibrate\nCAL.VER,019\nCAL.SYS,0000,'+\
                   ''.join([' 0.000000: '+'0.000000      0.000000,'*3]*27)
        cal_data2 = '\nCAL.SYS,0000,'+\
                    ''.join([' 0.000000: '+'0.000000      0.000000,'*3]*27)
                    
        cal_data = cal_data1+(cal_data2*(n_fn-1))
        cal_len = len(cal_data)
        
        cfid.write(struct.pack('<i', cal_len+2))
        cfid.write(struct.pack('<i', self._flag))
        cfid.write(struct.pack('<h', self._type_dict['cal']))
        cfid.write(cal_data[:-1]+'\n')
        cfid.write(struct.pack('<i', cal_len+2))
        
        #--> write data
        ts_block_len = int(ts_len)*n_fn*4+2
        
        #--> Need to scale the time series into counts cause that is apparently
        #    what MTFT24 expects
        #self.ts = self.ts.astype(np.int32)
        
        #--> make sure none of the data is above the allowed level
        self.ts[np.where(self.ts>2.14e9)] = 2.14e9
        self.ts[np.where(self.ts<-2.14e9)] = -2.14e9
        
        #--> write time series block
        cfid.write(struct.pack('<i', ts_block_len))
        cfid.write(struct.pack('<i', self._flag))
        cfid.write(struct.pack('<h', self._type_dict['ts']))
        
#        #--> need to pack the data as signed integers
#        for zz in range(ts_len):
#            cfid.write(struct.pack('<'+'i'*n_fn, *self.ts[zz]))

        ## write in chunks, should be faster
        chunk_size = 2048
        ts_flat = self.ts.flatten()
        for chunk in range(int(ts_len/chunk_size)):
            index_0 = chunk*chunk_size
            index_1 = (chunk+1)*chunk_size
            cfid.write(struct.pack('<'+'i'*chunk_size,
                                   *ts_flat[index_0:index_1]))                           
        # write the last bit
        cfid.write(struct.pack('<'+'i'*len(ts_flat[index_1:]),
                               *ts_flat[index_1:]))
        cfid.write(struct.pack('<i', ts_block_len))
        cfid.close()
        
        if self.verbose:
            print 'Saved File to: ', self.save_fn
        self.log_lines.append('='*72+'\n')
        self.log_lines.append('Saved File to: \n')
        self.log_lines.append(' '*4+'{0}\n'.format(self.save_fn))
        self.log_lines.append('='*72+'\n')
        
        #del self.ts
        #os.remove(temp_fn)
    
    #==================================================    
    def rewrite_cache_file(self):
        """
        rewrite a cache file if parameters changed
        
        assuming data that was read in is in counts.
        
        """
        self.save_fn_rw = mtfh.make_unique_filename(self.save_fn)
        
        cfid = file(self.save_fn_rw, 'wb+')
        
        n_fn = self.ts.shape[1]
        
        #--> write navigation records first        
        cfid.write(struct.pack('<i', self._nav_len))
        cfid.write(struct.pack('<i', self._flag))
        cfid.write(struct.pack('<h', self._type_dict['nav']))
        for nd in range(self._nav_len-2):
            cfid.write(struct.pack('<b', 0))
        cfid.write(struct.pack('<i', self._nav_len))
        
        #--> write meta data
        meta_str = ''.join([key+','+','.join(self.meta_data[key])+'\n' 
                             for key in np.sort(self.meta_data.keys())
                             if key != ''])
        
        meta_len = len(meta_str)
        
        cfid.write(struct.pack('<i', meta_len+2))
        cfid.write(struct.pack('<i', self._flag))
        cfid.write(struct.pack('<h', self._type_dict['meta']))
        cfid.write(meta_str)
        cfid.write(struct.pack('<i', meta_len+2))
        
        #--> write calibrations
        cal_data1 = 'HEADER.TYPE,Calibrate\nCAL.VER,019\nCAL.SYS,0000,'+\
                   ''.join([' 0.000000: '+'0.000000      0.000000,'*3]*1)
        cal_data2 = '\nCAL.SYS,0000,'+\
                    ''.join([' 0.000000: '+'0.000000      0.000000,'*3]*1)
                    
        cal_data = cal_data1+(cal_data2*(self.ts.shape[1]-1))
        cal_len = len(cal_data)
        
        cfid.write(struct.pack('<i', cal_len+2))
        cfid.write(struct.pack('<i', self._flag))
        cfid.write(struct.pack('<h', self._type_dict['cal']))
        cfid.write(cal_data[:-1]+'\n')
        cfid.write(struct.pack('<i', cal_len+2))
        
        #--> write data
        ts_block_len = self.ts.shape[0]*n_fn*4+2
        
        #--> make sure none of the data is above the allowed level
        self.ts[np.where(self.ts>2.14e9)] = 2.14e9
        self.ts[np.where(self.ts<-2.14e9)] = -2.14e9
        
        #--> write time series block
        cfid.write(struct.pack('<i', ts_block_len))
        cfid.write(struct.pack('<i', self._flag))
        cfid.write(struct.pack('<h', self._type_dict['ts']))
        for zz in range(self.ts.shape[0]):
            cfid.write(struct.pack('<'+'i'*n_fn, *self.ts[zz]))
                                
        cfid.write(struct.pack('<i', ts_block_len))
                 
        cfid.close()
        
        print 'Rewrote {0}\n to {1}'.format(self.save_fn, self.save_fn_rw)        
    
    #==================================================    
    def read_cache_metadata(self, cache_fn):
        """
        read only the meta data from the cache file
        """
        
        self.save_fn = cache_fn
        #open cache file to read in as a binary file
        cfid = file(cache_fn, 'rb')
        
        #read into a long string
        cdata = cfid.read(1050)
        
        #--> read navigation data
        nav_block = np.fromstring(cdata[0:self._stamp_len], 
                                  dtype=self._data_type)
        
        #get starting and ending indices for navigation block
        ii = int(self._stamp_len)
        jj = self._stamp_len+nav_block['len']-2
        self.nav_data = np.fromstring(cdata[ii:jj], dtype=np.int8)
        
        #get indicies for length of block
        ii = int(jj)
        jj = ii+4
        nav_len_check = np.fromstring(cdata[ii:jj], np.int32)
        if nav_len_check != nav_block['len']:
            if self.verbose:
                print 'Index for second navigation length is {0}'.format(ii)
            raise CacheNavigationError('Navigation length in data block are'
                                       'not equal: {0} != {1}'.format(
                                       nav_block['len'], nav_len_check))
        
        #--> read meta data
        ii = int(jj)
        jj = ii+self._stamp_len
        
        meta_block = np.fromstring(cdata[ii:jj], dtype=self._data_type)
        ii = int(jj)
        jj = ii+meta_block['len']-2
        self.meta_data = {}
        meta_list = cdata[ii:jj].split('\n')
        for mm in meta_list:
            mfind = mm.find(',')
            self.meta_data[mm[0:mfind]] = [ms.strip() for ms in 
                                            mm[mfind+1:].split(',')]
        
        #get index for second length test
        ii = int(jj)
        jj = ii+4
        meta_len_check = np.fromstring(cdata[ii:jj], dtype=np.int32)
        if meta_len_check != meta_block['len']:
            if self.verbose:
                print 'Index for second meta length is {0}'.format(ii)
            raise CacheMetaDataError('Meta length in data blocks are not '
                                     'equal: {0} != {1}'.format(
                                     meta_block['len'], meta_len_check))
        cfid.close()
        
    #==================================================
    def read_cache(self, cache_fn):
        """
        read a cache file
        
        """
        
        self.save_fn = cache_fn
        #open cache file to read in as a binary file
        cfid = file(cache_fn, 'rb')
        
        #read into a long string
        cdata = cfid.read()
        
        #--> read navigation data
        nav_block = np.fromstring(cdata[0:self._stamp_len], 
                                  dtype=self._data_type)
        
        #get starting and ending indices for navigation block
        ii = int(self._stamp_len)
        jj = self._stamp_len+nav_block['len']-2
        self.nav_data = np.fromstring(cdata[ii:jj], dtype=np.int8)
        
        #get indicies for length of block
        ii = int(jj)
        jj = ii+4
        nav_len_check = np.fromstring(cdata[ii:jj], np.int32)
        if nav_len_check != nav_block['len']:
            if self.verbose:
                print 'Index for second navigation length is {0}'.format(ii)
            raise CacheNavigationError('Navigation length in data block are'
                                       'not equal: {0} != {1}'.format(
                                       nav_block['len'], nav_len_check))
        
        #--> read meta data
        ii = int(jj)
        jj = ii+self._stamp_len
        
        meta_block = np.fromstring(cdata[ii:jj], dtype=self._data_type)
        ii = int(jj)
        jj = ii+meta_block['len']-2
        self.meta_data = {}
        meta_list = cdata[ii:jj].split('\n')
        for mm in meta_list:
            mfind = mm.find(',')
            self.meta_data[mm[0:mfind]] = mm[mfind+1:].split(',')
        
        #get index for second length test
        ii = int(jj)
        jj = ii+4
        meta_len_check = np.fromstring(cdata[ii:jj], dtype=np.int32)
        if meta_len_check != meta_block['len']:
            if self.verbose:
                print 'Index for second meta length is {0}'.format(ii)
            raise CacheMetaDataError('Meta length in data blocks are not'
                                     'equal: {0} != {1}'.format(
                                     meta_block['len'], meta_len_check))
        
        #--> read calibrations
        ii = int(jj)
        jj = ii+self._stamp_len
        cal_block = np.fromstring(cdata[ii:jj], dtype=self._data_type)
        
        ii = int(jj)
        jj = ii+cal_block['len']-2
        self.cal_data = cdata[ii:jj]
                
        
        ii = int(jj)
        jj = ii+4
        cal_len_check = np.fromstring(cdata[ii:jj], dtype=np.int32)
        if cal_len_check != cal_block['len']:
            if self.verbose:
                print 'Index for second cal length is {0}'.format(ii)
            raise CacheCalibrationError('Cal length in data blocks are not'
                                        'equal: {0} != {1}'.format(
                                        cal_block['len'], cal_len_check))
        
        #--> read data
        ii = int(jj)
        jj = ii+self._stamp_len
        
        ts_block = np.fromstring(cdata[ii:jj], dtype=self._data_type)
        
        #get time series data
        ii = int(jj)
        jj = ii+ts_block['len']-2
        self.ts = np.fromstring(cdata[ii:jj], dtype=self._ts_dtype)
        #resize time series to be length of each channel
        num_chn = len(self.meta_data['ch.cmp'.upper()])
        if self.ts.shape[0]%num_chn != 0:
            print 'Trimming TS by {0} points'.format(self.ts.shape[0]%num_chn)
        self.ts = np.resize(self.ts, (int(self.ts.shape[0]/num_chn), num_chn))
        
        ii = int(jj)
        jj = ii+4
        ts_len_check = np.fromstring(cdata[ii:jj], dtype=np.int32)
        if ts_len_check != ts_block['len']:
            if self.verbose:
                print 'Index for second ts length is {0}'.format(ii)
            raise CacheTimeSeriesError('ts length in data blocks are not'
                                       'equal: {0} != {1}'.format(
                                       ts_block['len'], ts_len_check))

    
#==============================================================================
# 
#==============================================================================
class ZenGPSError(Exception):
    """
    error for gps timing
    """
    pass

class ZenSamplingRateError(Exception):
    """
    error for different sampling rates
    """
    pass

class ZenInputFileError(Exception):
    """
    error for input files
    """
    pass

class CacheNavigationError(Exception):
    """
    error for navigation block in cache file
    """
    pass

class CacheMetaDataError(Exception):
    """
    error for meta data block in cache file
    """
    pass

class CacheCalibrationError(Exception):
    """
    error for calibration block in cache file
    """
    pass

class CacheTimeSeriesError(Exception):
    """
    error for time series block in cache file
    """
    pass

#==============================================================================
def rename_cac_files(station_dir, station='mb'):
    """
    rename and move .cac files to something more useful
    """
    fn_list = [os.path.join(station_dir, fn) for fn in os.listdir(station_dir)
                if fn[-4:].lower() == '.cac']
                    
    if len(fn_list) == 0:
        raise IOError('Could not find any .cac files')
        
    save_path = os.path.join(station_dir, 'Merged')
    if not os.path.exists(save_path) :
        os.mkdir(save_path)
    
    for fn in fn_list:
        cac_obj = Cache(fn)
        cac_obj.read_cache_metadata()
        station_name = '{0}{1}'.format(station, 
                                       cac_obj.metadata.station_number)
        station_date = cac_obj.metadata.gdp_date.replace('-', '')
        station_time = cac_obj.metadata.gdp_time.replace(':', '')
        new_fn = '{0}_{1}_{2}_{3:.0f}.cac'.format(station_name,
                                                  station_date, 
                                                  station_time,
                                                  cac_obj.metadata.ts_adfreq)
        new_fn = os.path.join(save_path, new_fn)
        shutil.move(fn, new_fn)
        print 'moved {0} to {1}'.format(fn, new_fn)
        
#==============================================================================
# copy and merge Z3D files from SD cards          
#==============================================================================
def copy_and_merge(station, z3d_save_path=None, merge_save_path=None, 
                   channel_dict={'1':'HX', '2':'HY', '3':'HZ','4':'EX', 
                                 '5':'EY', '6':'HZ'},
                   copy_date=None, copy_type='all'):
    """
    copy files from sd card then merge them together and run mtft24.exe
    
    Arguments:
    ----------
        **station** : string
                      full station name
                      
        **z3d_save_path** : string
                          full path to save .Z3D files
                          
        **merge_save_path** : string
                             full path to save merged cache files.  If None
                             saved to z3d_save_path\Merged
                             
        
        **channel_dict** : dictionary
                           keys are the channel numbers as strings and the
                           values are the component that corresponds to that 
                           channel, values are placed in upper case in the 
                           code
                           
        **copy_date** : YYYY-MM-DD
                        date to copy from depending on copy_type
                        
        **copy_type** : [ 'all' | 'before' | 'after' | 'on' ]
                        * 'all' --> copy all files on the SD card
                        * 'before' --> copy files before and on this date
                        * 'after' --> copy files on and after this date
                        * 'on' --> copy files on this date only
                        
    Returns:
    ------------
        **mfn_list** : list
                      list of merged file names
                      
    :Example: ::
    
        >>> import mpty.usgs.zen as zen
        >>> mfn_list = zen.copy_and_merge('mt01', z3d_save_path=r"/home/mt")
        >>> #copy only after a certain date
        >>> mfn_list = zen.copy_and_merge('mt01', z3d_save_path=r"/home/mt",\
                                          copy_date='2014/04/20', \
                                          copy_type='after')
    
    """
    
    #--> copy files from sd cards
    cpkwargs = {}
    cpkwargs['channel_dict'] = channel_dict
    cpkwargs['copy_date'] = copy_date
    cpkwargs['copy_type'] = copy_type
    if z3d_save_path != None:
        cpkwargs['save_path'] = z3d_save_path
    
    fn_list = zen.copy_from_sd(station, **cpkwargs)
    
    #--> merge files into cache files
    mfn_list = merge_3d_files(fn_list, save_path=merge_save_path)
    
    return mfn_list

#==============================================================================
# merge files into cache files for each sample block   
#==============================================================================
def merge_3d_files(fn_list, save_path=None, verbose=False, 
                   calibration_fn=r"c:\MT\amtant.cal"):
    """
    merge .Z3D files into cache files.  Looks through the file list and 
    Combines files with the same start time and sampling rate into a 
    cache file.  The calibration file is copied to the merged path for 
    later use with mtft24.exe processing code.
    
    Arguments:
    ----------
        **fn_list** : list
                     list of files to be merged
                     
        **save_path** : directory to save cach files to
        
        **verbose** : [ True | False ]
                      * True --> prints out information about the merging
                      * False--> surpresses print statements
        
        **calibration_fn** : string
                             full path to calibration file for ANT's
                             
    Outputs:
    --------
        **merged_fn_list** : nested list of files that were merged together
        
        A log file is written to save_path\station_merged_log.log that contains
        information about the files that were merged together.
        
     :Example: ::
    
        >>> import mtpy.usgs.zen as zen
        >>> fn_list = zen.copy_from_sd('mt01', save_path=r"/home/mt/survey_1")
        >>> zen.merge_3d_files(fn_list, calibration_fn=r"/home/mt/amtant.cal")
    
    """
    
    start_time = time.ctime()
    merge_list = np.array([[fn]+\
                          os.path.basename(fn)[:-4].split('_')
                          for fn in fn_list if fn.endswith('.Z3D')])
                              
    merge_list = np.array([merge_list[:,0], 
                          merge_list[:,1],  
                          np.core.defchararray.add(merge_list[:,2],
                                                   merge_list[:,3]),
                          merge_list[:,4],
                          merge_list[:,5]])
    merge_list = merge_list.T
            
    station_name = merge_list[0, 1]
                  
    time_counts = Counter(merge_list[:,2])
    time_list = time_counts.keys()
    
    log_lines = []
  
    merged_fn_list = []
    for tt in time_list:
        log_lines.append('+'*72+'\n')
        log_lines.append('Files Being Merged: \n')
        cache_fn_list = merge_list[np.where(merge_list == tt)[0], 0].tolist()
        
        for cfn in cache_fn_list:
            log_lines.append(' '*4+cfn+'\n')
        if save_path is None:
            save_path = os.path.dirname(cache_fn_list[0])
            
        else:
            save_path = save_path
            
        zc = ZenCache()
        zc.verbose = verbose
        zc.write_cache_file(cache_fn_list, save_path, station=station_name)
            
        for zt in zc.zt_list:
            try:
                log_lines.append(zt.log_lines)
            except AttributeError:
                pass
            
        merged_fn_list.append(zc.save_fn)
        log_lines.append('\n---> Merged Time Series Lengths and Start Time \n')
        log_lines.append(zc.log_lines)
        log_lines.append('\n')
    
    end_time = time.ctime()
    
    #copy the calibration file into the merged folder for mtft24
    try:
        copy_cal_fn = os.path.join(save_path, 'Merged',
                                 os.path.basename(calibration_fn))
    except:
        copy_cal_fn = os.path.join(save_path, os.path.basename(calibration_fn))
        
    shutil.copy(calibration_fn, copy_cal_fn)
    print 'copied {0} to {1}'.format(calibration_fn, copy_cal_fn)
    
    print 'Start time: {0}'.format(start_time)
    print 'End time:   {0}'.format(end_time)
    
    if os.path.basename(save_path) != 'Merged':
        log_fid = file(os.path.join(save_path, 'Merged', 
                                    station_name+'_Merged.log'), 'w')
    else:
        log_fid = file(os.path.join(save_path, station_name+'_Merged.log'),
                       'w')
    for line in log_lines:
        log_fid.writelines(line)
    log_fid.close()
        
    return merged_fn_list
