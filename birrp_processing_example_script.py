#!/usr/bin/env python
# coding: utf-8

# # Processing with BIRRP
# 
# This sample code shows how you might process MT time series with BIRRP.
# 
# - Step 1: Convert the raw time series into MTTS time series (mtpy.core.ts.MTTS), see below for an example.  This will depend on the instruments you use and therefore it is assumed here that your data are already in MTTS format.  
# 
# - Step 2: Gather information from each time series block and put that into a structured numpy array
# 
# - Step 3: Write a script file to run BIRRP
# 
# - Step 4: Run BIRRP
#     - **MAKE SURE YOU HAVE BIRRP INSTALLED ON YOUR COMPUTER**
#     - *IF YOU DON'T EMAIL ACHAVE@WHOI.EDU TO GET THE LATEST VERSION*
# 
# - Step 5: Convert BIRRP output to EDI

# ## Imports 
# *Note*: Be sure you have downloaded the latest version of MTPy from https://github.com/MTgeophysics/mtpy

# In[ ]:


import numpy as np
from mtpy.processing import birrp
from mtpy.core import ts


# ## Step 1: Convert data to MTTS format
# ### Make some example time series that are MTTS objects
# 
# - We will make one recording station and one remote reference station.
# - You can use this a template to put your own data into MTTS format.

# In[ ]:


### some generic parameters for making time series
sampling_rate = 64
n_samples = sampling_rate * 3600 * 4
### make a time array
t = np.arange(n_samples) * 1./sampling_rate


# In[ ]:


for comp in ['ex', 'ey', 'hx', 'hy', 'hz']:
    ts_obj = ts.MTTS()
    if 'x' in comp:
        ts_obj.azimuth = 0
    elif 'y' in comp:
        ts_obj.azimuth = 90
    ts_obj.component = comp
    ts_obj.coordinate_system = 'geomagnetic'
    ts_obj.datum = 'WGS84'
    ts_obj.declination = -11.5
    ts_obj.data_logger = 'example'
    ts_obj.instrument_id = 'test'
    ts_obj.lat = 40.0
    ts_obj.lon = -120.00
    ts_obj.sampling_rate = sampling_rate
    ts_obj.start_time_utc = '2018-01-01T12:00:00.00 UTC'
    ts_obj.station = 'MT01'
    ts_obj.units = 'mV'
    if 'h' in comp:
        ts_obj.calibration_fn = 'coil_calibration_file'
    if 'e' in comp:
        ts_obj.dipole_length = 100.0
    ### make a somewhat realistic time series
    ts_obj.ts = np.sum([amp*np.sin(2*np.pi*omega*t+phi) for amp, omega, phi in zip(np.random.random(50), np.logspace(-3, 3, num=50), np.random.random(50))], axis=0)
    ts_obj.write_ascii_file('sample_station_TS.{0}'.format(comp.upper()))
    ### make remote reference stations
    if comp in ['hx', 'hy']:
        ts_obj.ts = np.sum([amp*np.sin(2*np.pi*omega*t+phi) for amp, omega, phi in zip(np.random.random(50), np.logspace(-3, 3, num=50), np.random.random(50))], axis=0)
        ts_obj.write_ascii_file('sample_rr_station_TS.{0}'.format(comp.upper()))


# # Step 2: Gather the time series into a structured numpy array to put into BIRRP

# ### add any BIRRP parameters
# 
# *see BIRRP documentation for descriptions of these parameters.Below are some that you might change.*

# In[ ]:


birrp_param_dict = {'c2threshb' : 0.45, 'c2threshe': 0.45, 'ainuin' : .9995, 'ainlin' : 0.0005, 'nar' : 7, 'tbw' : 2}


# In[ ]:


script_obj = birrp.ScriptFile(**birrp_param_dict)

### set sampling rate (negative numbers for samples/second)
script_obj.deltat = -1 * sampling_rate

### make an empty array with data type that the script file wants,
### length of 7 for 5 station components and 1 remote reference dataion with 2 remote reference components
### need to make it [number_of_blocks, 7], here we only have one time series block
### if you have multiple blocks add an array
script_obj.fn_arr = np.array([np.zeros(7, dtype=script_obj._fn_dtype)])

### fill the array from the metadata within the MTTS files
for ii, comp in enumerate(['ex', 'ey', 'hx', 'hy', 'hz']):
    ### read in time series file
    ts_obj = ts.MTTS()
    ts_obj.read_ascii_header('sample_station_TS.{0}'.format(comp.upper()))
    script_obj.fn_arr[0][ii]['fn'] = ts_obj.fn
    script_obj.fn_arr[0][ii]['nread'] = ts_obj.n_samples
    script_obj.fn_arr[0][ii]['nskip'] = 22 ### birrp only reads in numbers so need to skip the header 
    script_obj.fn_arr[0][ii]['comp'] = ts_obj.component
    script_obj.fn_arr[0][ii]['calibration_fn'] = ts_obj.calibration_fn
    script_obj.fn_arr[0][ii]['rr'] = False
    script_obj.fn_arr[0][ii]['rr_num'] = 0
    script_obj.fn_arr[0][ii]['start_dt'] = ts_obj.start_time_utc
for ii, comp in enumerate(['hx', 'hy'], 5):
        ### read in time series file
        ts_obj = ts.MTTS()
        ts_obj.read_ascii_header('sample_rr_station_TS.{0}'.format(comp.upper()))
        script_obj.fn_arr[0][ii]['fn'] = ts_obj.fn
        script_obj.fn_arr[0][ii]['nread'] = ts_obj.n_samples
        script_obj.fn_arr[0][ii]['nskip'] = 22 ### birrp only reads in numbers so need to skip the header 
        script_obj.fn_arr[0][ii]['comp'] = ts_obj.component
        script_obj.fn_arr[0][ii]['calibration_fn'] = ts_obj.calibration_fn
        script_obj.fn_arr[0][ii]['rr'] = True
        script_obj.fn_arr[0][ii]['rr_num'] = 1 
        script_obj.fn_arr[0][ii]['start_dt'] = ts_obj.start_time_utc

### make sure we assembled the array properly
script_obj._validate_fn_arr()
print(script_obj.fn_arr)


# ## Step 3: Write script file to run BIRRP

# In[ ]:


script_obj.write_script_file('example_birrp.script')


# ### Write a configuration file so you remember what you did

# In[ ]:


script_obj.write_config_file('example_birrp_config.cfg')


# ## Step 4: Run BIRRP

# In[ ]:


birrp_exe_path = '/home/path/to/birrp/executable'


# **NOTE**: this will not work you need to fill in the correct path to BIRRP executable

# In[ ]:


birrp.run(birrp_exe_path, 'example_birrp.script')


# ## Step 5: Convert BIRRP outputs to an EDI file
# 
# * You should have a survey configuration file with the format:
# 
#     > [station_name]
#        metadata_key = metadata_value
#     
#     * For Example:
#     
#         > [MT01]
#             b_instrument_amplification = 1
#             b_instrument_type = coil
#             b_logger_gain = 1
#             b_logger_type = zen
#             b_xaxis_azimuth = 0
#             b_yaxis_azimuth = 90
#             box = 26
#             date = 2015/06/09
#             e_instrument_amplification = 1
#             e_instrument_type = Ag-Agcl electrodes
#             e_logger_gain = 1
#             e_logger_type = zen
#             e_xaxis_azimuth = 0
#             e_xaxis_length = 100
#             e_yaxis_azimuth = 90
#             e_yaxis_length = 100
#             elevation = 2113.2
#             hx = 2274
#             hy = 2284
#             hz = 2254
#             lat = 37.7074236995
#             location = Earth
#             lon = -118.999542099
#             network = USGS
#             notes = Generic config file
#             rr_box = 25
#             rr_date = 2015/06/09
#             rr_hx = 2334
#             rr_hy = 2324
#             rr_lat = 37.6909139779
#             rr_lon = -119.028707542
#             rr_station = 302
#             sampling_interval = all
#             save_path = \home\mtdata\survey_01\mt_01
#             station = 300
#             station_type = mt
#         
#         
#     
#     
# * fill in the file paths below to make this work.
#     

# In[ ]:


j2edi = birrp.J2EDI()
j2edi.survey_config_fn = r'/path/to/survey/configuration/file'
j2edi.birrp_config_fn = r'/path/to/birrp/configuration/file' ### here it would be example_birrp_config.cfg
j2edi.birrp_dir = r'/path/to/station/birrp/folder' ### here it would be the current directory
j2edi.write_edi_file(station='station_name')

