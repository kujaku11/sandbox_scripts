# -*- coding: utf-8 -*-
"""
Created on Tue May 26 13:29:59 2015

@author: jpeacock-pr
"""

import mtpy.processing.birrp as birrp
import mtpy.utils.configfile as mtcfg
import mtpy.utils.filehandling as mtfh
import os
import mtpy.usgs.zen as zen
import numpy as np
import time
import mtpy.imaging.plotnresponses as plotnresponses
import mtpy.imaging.plotresponse as plotresponse

#==============================================================================
datetime_fmt = '%Y-%m-%d,%H:%M:%S'
datetime_sec = '%Y-%m-%d %H:%M:%S'

#==============================================================================
# make a class to go from Z3d to .edi
#==============================================================================
class BIRRP_processing(object):
    """
    configuration file for birrp processing
    """
    
    def __init__(self, **kwargs):
        self.jmode = 0
        self.nskip = 1
        self.nskipr = 1
        self.calibration_path = kwargs.pop('calibration_path', 
                                         r"d:\Peacock\MTData\Ant_calibrations")
        self.calibration_list = ['2254', '2264', '2274', '2284', '2294',
                                '2304', '2314', '2324', '2334', '2344']
                                
        self.mcomps = 5
        self.elecori = "EX,EY"
        self.tbw = 2
        self.ainuin = .9999
        self.magtype = 'bb'
        self.nfft = 2**18
        self.nsctmax = 14
        self.ilev = 0
        self.nar = 5
        self.nrr = 0
        self.c2thresb = 0.45        
        
    def get_calibrations(self, calibration_path=None):
        """
        get coil calibrations
        """
        if calibration_path is not None:
            self.calibration_path = calibration_path
            
        calibration_dict = {}
        for cal_fn in os.listdir(self.calibration_path):
            for cal_num in self.calibration_list:
                if cal_num in cal_fn:
                    calibration_dict[cal_num] = \
                                    os.path.join(self.calibration_path, cal_fn)
                    break
        return calibration_dict
        
    def get_processing_dict(self, fn_birrp_list, hx=2284, hy=2284, hz=2284):
        """
        from fn_birrp_arr make a processing dictionary to input into writing
        a birrp script file
        
        fn_birrp_list = fn_birrp_arr[df]
        """
        comp_dict = {4:{'EX':0, 'EY':1, 'HX':2, 'HY':3},
                     5:{'EX':0, 'EY':1, 'HZ':2, 'HX':3, 'HY':4}}
        rr_comp_dict = {'HX':0, 'HY':1}
        
        self.fn_list = [fn_list['fn'] for fn_list in fn_birrp_list]
        # need to sort the fn list so that the files are in the correct
        # order for input and output as defined by birrp
        for ii, f_list in enumerate(self.fn_list):
            sort_list = list(f_list)
            num_comps = len(f_list)
            for fn in f_list:
                key = fn[-2:]
                sort_list[comp_dict[num_comps][key.upper()]] = fn
        self.fn_list[ii] = sort_list
            
        # get remote reference file names, same as input, just hx and hy
        self.rrfn_list = []
        for fn_list in fn_birrp_list:
            rr_list = [1, 2]
            for fn in fn_list['fn']:
                key = fn[-2:].upper()
                if key == 'HX' or key == 'HY':
                   rr_list[rr_comp_dict[key]] = fn
            self.rrfn_list.append(rr_list)

        self.nread = [fn_list['npts'].min() for fn_list in fn_birrp_list] 
        self.mcomps = len(fn_birrp_list[0])
        
        if self.mcomps == 5:
            self.magori = "HZ,HX,HY"
            
        elif self.mcomps == 4:
            self.magori = "HX,HY"
        else:
            raise IOError('Number of components is {0}'.format(self.mcomps))
        
        # get calibrations for coil responses        
        cal_dict = self.get_calibrations()
        #get calibration files
        #--> HX                                                 
        try:
            self.hx_cal = cal_dict[str(hx)]
            self.rrhx_cal = cal_dict[str(hx)]
        except KeyError:
            print 'Did not find HX calibration for {0}'.format(hx)
            self.hx_cal = cal_dict['2284'] 
            self.rrhx_cal = cal_dict['2284'] 
            print 'Setting calibration coil number to 2284 as default.'            
        #--> HY                                                 
        try:
            self.hy_cal = cal_dict[str(hy)]
            self.rrhy_cal = cal_dict[str(hy)]
        except KeyError:
            print 'Did not find HX calibration for {0}'.format(hy)
            self.hy_cal = cal_dict['2284'] 
            self.rrhy_cal = cal_dict['2284'] 
            print 'Setting calibration coil number to 2284 as default.'            
        #--> HZ                                                 
        try:
            self.hz_cal = cal_dict[str(hz)]
        except KeyError:
            print 'Did not find HX calibration for {0}'.format(hz)
            self.hz_cal = cal_dict['2284'] 
            print 'Setting calibration coil number to 2284 as default.'            
        
        return self.__dict__
        
        
class Survey_Config(object):
    """
    survey config class
    """
    def __init__(self, **kwargs):
        self.b_instrument_amplification = 1
        self.b_instrument_type = 'coil'
        self.b_logger_gain = 1
        self.b_logger_type = 'zen'
        self.b_xaxis_azimuth = 0
        self.b_yaxis_azimuth = 90
        self.box = 24
        self.date = '01/01/00'
        self.e_instrument_amplification = 1
        self.e_instrument_type = 'Cu-CuSO4 electrodes'
        self.e_logger_gain = 1
        self.e_logger_type = 'zen'
        self.e_xaxis_azimuth = 0
        self.e_xaxis_length = 100
        self.e_yaxis_azimuth = 90
        self.e_yaxis_length = 100
        self.elevation = 2113.2
        self.hx = 2324
        self.hy = 2314
        self.hz = 2334
        self.lat = 37.8861
        self.location = 'Earth'
        self.lon = -119.05417
        self.network = 'USGS'
        self.notes = 'Generic config file'
        self.sampling_interval = 'all'
        self.station = 'mb000'
        self.station_type = 'mt'
        self.save_path = None
        
        for key in kwargs:
            setattr(self, key, kwargs[key])
    
    def write_survey_config_file(self, save_path=None):
        """
        write a survey config file to save path
        """
        
        if save_path is not None:
            self.save_path = save_path
        fn = os.path.join(self.save_path, '{0}.cfg'.format(self.station))
        mtcfg.write_dict_to_configfile({self.station:self.__dict__}, fn)
        
        print 'Wrote survey config file to {0}'.format(fn)
        
        return fn


class Z3D_to_edi(object):
    """
    go from z3d files to .edi
    """
    
    def __init__(self, station_dir=None, **kwargs):
        
        self.station_dir = station_dir
        #ZenBIRRP.__init__(self, self.station_dir)
        self.survey_config = Survey_Config(save_path=self.station_dir)
        self.survey_config_fn = None
        self.birrp_config_fn = None

        
    def make_survey_config_file(self, survey_config_dict=None):
        """
        make a survey configuration file from the data
        """
        
        self.survey_config_fn = self.survey_config.write_survey_config_file()
        
    def get_schedules_fn_from_dir(self, station_ts_dir):
        """
        get the birrp fn list from a directory of TS files
        """
        
        self.station_dir = station_ts_dir
        
        fn_arr = np.zeros(len(os.listdir(station_ts_dir)),
                          dtype=[('fn','|S100'),
                                 ('npts',np.int),
                                 ('start_dt','|S19'),
                                 ('end_dt','|S19'),
                                 ('df', np.float)])
        fn_count = 0
        for fn in os.listdir(station_ts_dir):
            fn = os.path.join(station_ts_dir, fn)
            try:
                header_dict = mtfh.read_ts_header(fn)
                fn_arr[fn_count]['fn'] = fn
                fn_arr[fn_count]['npts'] = header_dict['nsamples']
                fn_arr[fn_count]['df'] = header_dict['samplingrate']
                start_sec = header_dict['t_min']
                num_sec = float(header_dict['nsamples'])/\
                                                   header_dict['samplingrate']
                fn_arr[fn_count]['start_dt'] = time.strftime(datetime_fmt, 
                                                time.localtime(start_sec)) 
                fn_arr[fn_count]['end_dt'] = time.strftime(datetime_fmt, 
                                                time.localtime(start_sec+\
                                                num_sec))
                fn_count += 1
            except zen.mtex.MTpyError_ts_data:
                print '  Skipped {0}'.format(fn)
            except zen.mtex.MTpyError_inputarguments:
                print '  Skipped {0}'.format(fn)
        
        # be sure to trim the array
        fn_arr = fn_arr[np.nonzero(fn_arr['npts'])]
        
        return self.get_schedules_fn(fn_arr)
            
        
    def get_schedules_fn(self, fn_arr):
        """
        seperate out the different schedule blocks and frequencies so the
        can be processed
        
        Returns
        ---------
            **schedule_fn_dict** : dictionary
                                   keys are sampling rates and values are
                                   lists of file names for each schedule
                                   block up to 3 blocks
        """
        # get the sampling rates used
        s_keys = set(fn_arr['df'])
        
        # make a dictionary with keys as the sampling rates 
        s_dict = dict([(skey, []) for skey in s_keys])
        
        # loop over the sampling rates and find the schedule blocks
        for df in s_keys:
            # find startind dates for sampling rate
            s_dates = set(fn_arr['start_dt'][np.where(fn_arr['df']==df)])
            for sdate in s_dates:
                s_fn_arr = fn_arr[np.where(fn_arr['start_dt']==sdate)]
                s_fn_birrp_arr = np.zeros(len(s_fn_arr), 
                                          dtype=[('fn','|S100'),
                                                 ('npts',np.int),
                                                 ('start_dt','|S19'),
                                                 ('end_dt','|S19')])
                s_fn_birrp_arr['fn'] = s_fn_arr['fn']
                s_fn_birrp_arr['npts'][:] = s_fn_arr['npts'].min()
                s_fn_birrp_arr['start_dt'][:] = sdate
                start_seconds = time.mktime(time.strptime(sdate, 
                                                          datetime_fmt))
 
                end_seconds = start_seconds+s_fn_arr['npts'].min()/float(df)
                s_fn_birrp_arr['end_dt'][:] = time.strftime(datetime_sec,
                                                time.localtime(end_seconds))  
                s_dict[df].append(s_fn_birrp_arr)
        
        return s_dict
        
    def make_mtpy_ascii_files(self, station_dir=None, fmt='%.8', 
                              station_name='mb', notch_dict={},
                              df_list=None): 
        """
        makes mtpy_mt files from .Z3D files
        
        Arguments:
        -----------
            **dirpath** : full path to .Z3D files
            
            **station_name** : prefix for station names
            
            **fmt** : format of data numbers for mt_files
            
        Outputs:
        --------
            **fn_arr** : np.ndarray(file, length, df, start_dt)
            
        :Example: ::
        
            >>> import mtpy.usgs.zen as zen
            >>> fn_list = zen.copy_from_sd('mt01')
            >>> mtpy_fn = zen.make_mtpy_files(fn_list, station_name='mt')
        """
        
        if station_dir is not None:
            self.station_dir = station_dir
            
        fn_list = [os.path.join(self.station_dir, fn) 
                    for fn in os.listdir(self.station_dir) 
                    if fn[-4:] == '.Z3D']
        if len(fn_list) == 0:
            raise IOError('Could not find any .Z3D files in {0}'.format(
                            self.station_dir))
                            
        # make an array that has all the information about each file
        fn_arr = np.zeros(len(fn_list), 
                          dtype=[('station','|S6'), 
                                 ('npts',np.int), 
                                 ('df', np.int),
                                 ('start_dt', '|S22'), 
                                 ('comp','|S2'),
                                 ('fn','|S100')])
        fn_lines = []
                                 
        for ii, fn in enumerate(fn_list):
            if df_list is not None:
               zd = zen.Zen3D(fn)
               zd.read_header()
               if zd.header.ad_rate in df_list:
                   zd.read_z3d()
               else:
                   continue
            else:
                zd = zen.Zen3D(fn)
                zd.read_z3d()
            
            if zd.metadata.ch_cmp.lower() == 'hx':
                self.survey_config.hx = zd.metadata.ch_number
            if zd.metadata.ch_cmp.lower() == 'hy':
                self.survey_config.hy = zd.metadata.ch_number
            if zd.metadata.ch_cmp.lower() == 'hz':
                self.survey_config.hz = zd.metadata.ch_number
            if zd.metadata.ch_cmp.lower() == 'ex':
                self.survey_config.e_xaxis_length = zd.metadata.ch_length
            if zd.metadata.ch_cmp.lower() == 'ey':
                self.survey_config.e_yaxis_length = zd.metadata.ch_length

            # get station configuration from the first Z3D file            
            if ii == 0:
                self.survey_config.lat = zd.header.lat
                self.survey_config.lon = zd.header.long
                self.survey_config.date = zd.schedule.Date.replace('-','/')
                self.survey_config.box = int(zd.header.box_number)
            
            #write mtpy mt file
            zd.write_ascii_mt_file(notch_dict=notch_dict)
            
            #create lines to write to a log file                       
            station = zd.metadata.rx_xyz0.split(':')[0]
            fn_arr[ii]['station'] = '{0}{1}'.format(station_name, station)
            fn_arr[ii]['npts'] = zd.time_series.shape[0]
            fn_arr[ii]['df'] = zd.df
            fn_arr[ii]['start_dt'] = zd.zen_schedule
            fn_arr[ii]['comp'] = zd.metadata.ch_cmp.lower()
            fn_arr[ii]['fn'] = zd.fn_mt_ascii
            fn_lines.append(''.join(['--> station: {0}{1}\n'.format(station_name, station),
                                     '    ts_len = {0}\n'.format(zd.time_series.shape[0]),
                                     '    df = {0}\n'.format(zd.df),
                                     '    start_dt = {0}\n'.format(zd.zen_schedule),
                                     '    comp = {0}\n'.format(zd.metadata.ch_cmp),
                                     '    fn = {0}\n'.format(zd.fn)]))
                                     
        self.station_dir = os.path.join(self.station_dir, 'TS')
        self.survey_config.save_path = self.station_dir
        # write survey configuration file
        self.survey_config.write_survey_config_file()
        
            
        return fn_arr[np.nonzero(fn_arr['npts'])], fn_lines
        
    def write_script_files(self, fn_birrp_dict, save_path=None):
        """
        write a script file from a generic processing dictionary
        """
        
        if save_path is None:
            save_path = os.path.join(self.station_dir, 'BF')
        if not os.path.exists(save_path):
            os.mkdir(save_path)
            
        s_keys = fn_birrp_dict.keys()
        script_fn_list = []
        for skey in s_keys:
            bf_path = os.path.join(save_path, '{0:.0f}'.format(skey))
            fn_birrp_arr = fn_birrp_dict[skey]
            pro_obj = BIRRP_processing()
            pro_obj.station = self.survey_config.station
            pro_obj.deltat = -float(skey)
            pro_dict = pro_obj.get_processing_dict(fn_birrp_arr, 
                                                   hx=self.survey_config.hx,
                                                   hy=self.survey_config.hy,
                                                   hz=self.survey_config.hz)
            
            #write script file using mtpy.processing.birrp    
            script_fn, birrp_dict = birrp.write_script_file(pro_dict,
                                                        save_path=bf_path)
                                                        
            script_fn_list.append(script_fn)
            
            cfg_fn = mtfh.make_unique_filename('{0}_birrp_params.cfg'.format(
                                                                 script_fn[:-7]))
                                                                 
            mtcfg.write_dict_to_configfile(birrp_dict, cfg_fn)
            print 'Wrote BIRRP config file for edi file to {0}'.format(cfg_fn)
    
            self.birrp_config_fn = cfg_fn
        
        return script_fn_list   
        
    def run_birrp(self, script_fn_list=None, 
                  birrp_exe=r"c:\MinGW32-xy\Peacock\birrp52\birrp52_3pcs6e9pts_big.exe"):
        """
        run birrp given the specified files
        
        """
        
        if script_fn_list is None:
            raise IOError('Need to input a script file or list of script files')
        
        if birrp_exe is not None:
            self.birrp_exe = birrp_exe
            
            
        if type(script_fn_list) is list:
            self.edi_fn = []
            for script_fn in script_fn_list:
                birrp.run(self.birrp_exe, script_fn)
                
                output_path = os.path.dirname(script_fn)
                self.edi_fn.append(self.write_edi_file(output_path, 
                                      survey_config_fn=self.survey_config_fn,
                                      birrp_config_fn=self.birrp_config_fn))
        elif type(script_fn_list) is str:
            birrp.run(self.birrp_exe, script_fn_list)
            
            output_path = os.path.dirname(script_fn)
            self.edi_fn = self.write_edi_file(output_path, 
                                      survey_config_fn=self.survey_config_fn,
                                      birrp_config_fn=self.birrp_config_fn)
        
    def write_edi_file(self, birrp_output_path, survey_config_fn=None, 
                       birrp_config_fn=None):
        """
        write an edi file from outputs of birrp
        """
        if self.survey_config_fn is not None:
            self.survey_config_fn = survey_config_fn        
        
        if self.survey_config_fn is None:
            ts_find = birrp_output_path.find('TS')
            if ts_find > 0:
                ts_dir = birrp_output_path[0:ts_find+2]
                for fn in os.listdir(ts_dir):
                    if fn[-4:] == '.cfg':
                        self.survey_config_fn = os.path.join(ts_dir, fn)
        
        edi_fn = birrp.convert2edi(self.survey_config.station, 
                                   birrp_output_path, 
                                   self.survey_config_fn, 
                                   self.birrp_config_fn)
        
        return edi_fn
        
    def plot_responses(self, edi_fn_list=None):
        """
        
        plot all the edi files that were created.
        """
        if edi_fn_list is not None:
            self.edi_fn = edi_fn_list
            

        
        if type(self.edi_fn) is list:
            # check file lengths to make sure there are no zero length files
            for edi_fn in self.edi_fn:
                fn_size = os.path.getsize(edi_fn)
                if fn_size < 3000:
                    self.edi_fn.remove(edi_fn)
                if len(self.edi_fn) == 0:
                    raise ValueError('No good .edi files where produced')
            resp_plot = plotnresponses.PlotMultipleResponses(fn_list=self.edi_fn,
                                                         plot_style='compare',
                                                         plot_tipper='yri')
        elif type(self.edi_fn) is str:
            if os.path.getsize(self.edi_fn) < 3000:
                raise ValueError('No good .edi files where produced')
            resp_plot = plotresponse.PlotResponse(fn=self.edi_fn,
                                                  plot_tipper='yri')
                                                         
        return resp_plot
 
    def process_data(self, df_list=None):
        """
        from the input station directory, convert files to ascii, run through
        BIRRP, convert to .edi files and plot
        """
        
        st = time.time()
        
        if df_list is not None:
            if type(df_list) is float or type(df_list) is int or\
               type(df_list) is str:
               df_list = [df_list] 
        
        # make files into mtpy files
        z3d_fn_list, log_lines = self.make_mtpy_ascii_files(df_list=list(df_list))
        
        # get all information from mtpy files
        schedule_dict = self.get_schedules_fn(z3d_fn_list)
            
        # write script files for birrp
        sfn_list = self.write_script_files(schedule_dict)
        
        # run birrp
        self.run_birrp(sfn_list)
        
        # plot the output
        r_plot = self.plot_responses()
        
        et = time.time()
        print 'took {0} seconds'.format(et-st)
        
        return r_plot
    
    
#==============================================================================
# run a test
#==============================================================================

#st = time.time()

# give it a directory
station_path = r"d:\Peacock\MTData\Test\mb666"

# initialize an object
ztest = Z3D_to_edi(station_path)
ztest.process_data(df_list=[256, 1024])

## make files into mtpy files
#z3d_fn_list, log_lines = ztest.make_mtpy_ascii_files()
#
## get all information from mtpy files
#schedule_dict = ztest.get_schedules_fn(z3d_fn_list)
#
##schedule_dict = ztest.get_schedules_fn_from_dir(os.path.join(station_path, 'TS'))
#
## write script files for birrp
#sfn_list = ztest.write_script_files(schedule_dict)
#
## run birrp
#ztest.run_birrp(sfn_list)
#
## plot the output
#r_plot = ztest.plot_responses()
#
#et = time.time()
#print 'took {0} seconds'.format(et-st)
