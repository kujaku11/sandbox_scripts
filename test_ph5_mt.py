# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 10:12:20 2019

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
import numpy as np

#from ph5.utilities import obspytoph5
from ph5.core import experiment
from mtpy.core import ts as mtts

# =============================================================================
# make a time series
# =============================================================================

#import numpy as np
#from obspy.core import Trace, UTCDateTime
ts_obj = mtts.MTTS()
ts_obj.station = 'mt001'
ts_obj.azimuth = 0
ts_obj.component = 'EX'
ts_obj.coordinate_system = 'geomagnetic north'
ts_obj.data_logger = 'IRIS001'
ts_obj.datum = 'WGS84'
ts_obj.declination = 11.5
ts_obj.dipole_length = 97.5
ts_obj.gain = 1
ts_obj.instrument_id = 'electrode01'
ts_obj.lat = 40.0
ts_obj.lon = -115.00
ts_obj.elev = 1000
ts_obj.start_time_utc = '2019-05-29T01:00:00'
ts_obj.sampling_rate = 256.0
ts_obj.ts = np.random.ranf(256*3600*4)

## now we have our data let's set up PH5
## open ph5 for editing
path = '.'
ph5_object = experiment.ExperimentGroup(
    nickname='master.ph5',
    currentpath=path)
ph5_object.ph5open(True)
ph5_object.initgroup()

# open mini file
mini_num = str(1).zfill(5)
filename = "miniPH5_{0}.ph5".format(mini_num)
exrec = experiment.ExperimentGroup(nickname=filename,
                                   currentpath=ph5_object.currentpath)
exrec.ph5open(True)
exrec.initgroup()

# get node reference or create new node
d = mini_handle.ph5_g_receivers.getdas_g(entry['serial'])
if not d:
    d, t, r, ti = exrec.ph5_g_receivers.newdas(entry['serial'])
### fill das table, what ever that is
das['time/ascii_s'] = trace.stats.starttime    
das['time/epoch_l'] = (int(time))
das['time/micro_seconds_i'] = microsecond
das['time/type_s'] = 'BOTH' 
if (trace.stats.sampling_rate >= 1 or
        trace.stats.sampling_rate == 0):
    das['sample_rate_i'] = trace.stats.sampling_rate
    das['sample_rate_multiplier_i'] = 1
else:
    das['sample_rate_i'] = 0
    das['sample_rate_multiplier_i'] = (1 /trace.stats.sampling_rate)  
    
channel_list = list(trace.stats.channel)
if channel_list[2] in ({'3', 'Z', 'z'}):
    das['channel_number_i'] = 3
elif channel_list[2] in (
        {'2', 'E', 'e'}):
    das['channel_number_i'] = 2
elif channel_list[2] in (
        {'1', 'N', 'n'}):
    das['channel_number_i'] = 1
elif channel_list[2].isdigit():
    das['channel_number_i'] = channel_list[2]
elif trace.stats.channel == 'LOG':
    das['channel_number_i'] = -2
    das['sample_rate_i'] = 0
    das['sample_rate_multiplier_i'] = 1
else:
    das['channel_number_i'] = -5
if in_type == 'file':
    das['raw_file_name_s'] = file_tuple[0]
else:
    das['raw_file_name_s'] = 'obspy_stream'
if trace.stats.channel == 'LOG':
    das['sample_count_i'] = 0
else:
    das['sample_count_i'] = trace.stats.npts

# figure out receiver and response n_i
for array_entry in self.arrays:
    if (array_entry['sample_rate_i'] ==
            trace.stats.sampling_rate and
            array_entry['channel_number_i'] ==
            das['channel_number_i'] and
            array_entry['id_s'] == trace.stats.station):
        das['receiver_table_n_i'] =\
            array_entry['receiver_table_n_i']
        das['response_table_n_i'] =\
            array_entry['response_table_n_i']

# Make sure we aren't overwriting a data array
while True:
    next_ = str(count).zfill(5)
    das['array_name_data_a'] = "Data_a_{0}".format(
        next_)
    node = mini_handle.ph5_g_receivers.find_trace_ref(
        das['array_name_data_a'])
    if not node:
        break
    count = count + 1
    continue
    
### fill index table
# start populating das table and data arrays
index_t_entry['start_time/ascii_s'] = (trace.stats.starttime.isoformat())
time = timedoy.fdsn2epoch(trace.stats.starttime.isoformat(), fepoch=True)
microsecond = (time % 1) * 1000000

index_t_entry['start_time/epoch_l'] = (int(time))
index_t_entry['start_time/micro_seconds_i'] = (
    microsecond)
index_t_entry['start_time/type_s'] = 'BOTH'
time = timedoy.fdsn2epoch(
    trace.stats.endtime.isoformat(), fepoch=True)
microsecond = (time % 1) * 1000000
index_t_entry['end_time/ascii_s'] = (
    trace.stats.endtime.isoformat())
index_t_entry['end_time/epoch_l'] = (int(time))
index_t_entry['end_time/micro_seconds_i'] = (
    microsecond)
index_t_entry['end_time/type_s'] = 'BOTH'
now = UTCDateTime.now()
index_t_entry['time_stamp/ascii_s'] = (
    now.isoformat())
time = timedoy.fdsn2epoch(
    now.isoformat(), fepoch=True)
microsecond = (time % 1) * 1000000
index_t_entry['time_stamp/epoch_l'] = (int(time))
index_t_entry['time_stamp/micro_seconds_i'] = (
    int(microsecond))
index_t_entry['time_stamp/type_s'] = 'BOTH'

if time_corrected:
    time_t['corrected_i'] = 1

if time_t:
    self.time_t.append(time_t)
    
if correction or time_corrected:
    time_t['das/serial_number_s'] = entry['serial']

    if in_type == 'file':
        time_t['description_s'] = file_tuple[0]
    else:
        time_t['description_s'] = (
                str(trace.stats.station) +
                str(trace.stats.channel))
    # SEED time correction
    # units are 0.0001 seconds per unit
    time_t['offset_d'] = flags["timing_correction"] * 0.0001
    time_t['start_time/epoch_l'] =index_t_entry['start_time/epoch_l']
    time_t['start_time/micro_seconds_i'] = index_t_entry['start_time/micro_seconds_i']
    time_t['end_time/epoch_l'] = index_t_entry['end_time/epoch_l']
    time_t['end_time/micro_seconds_i'] = index_t_entry['end_time/micro_seconds_i']
    length = trace.stats.npts * trace.stats.delta
    if length != 0:
        time_t['slope_d'] = time_t['offset_d'] / length
    else:
        time_t['slope_d'] = 0

mini_handle.ph5_g_receivers.setcurrent(d)
data = array(trace.data)
if trace.stats.channel == 'LOG':
    mini_handle.ph5_g_receivers.newarray(
        das['array_name_data_a'], data, dtype='|S1',
        description=None)
else:
    mini_handle.ph5_g_receivers.newarray(
        das['array_name_data_a'], data, dtype='int32',
        description=None)
mini_handle.ph5_g_receivers.populateDas_t(das)

index_t_entry['external_file_name_s'] = "./{}".format(
    mini_name)
das_path = "/Experiment_g/Receivers_g/" \
           "Das_g_{0}".format(entry['serial'])
index_t_entry['hdf5_path_s'] = das_path
index_t_entry['serial_number_s'] = entry['serial']

index_t.append(index_t_entry)
# Don't forget to close minifile
mini_handle.ph5close()
#LOGGER.info('Finished processing {0}'.format(file_tuple[0]))

# last thing is to return the index table so far.
# index_t will be populated in main() after all
# files are loaded
#return "done", index_t


## first let's read our data file into a numpy array
#data = list()
#fh = open('data.txt')
#for line in fh:
#    data.append(int(line.strip('\r\n')))
#fh.close()
#data = np.array(data, dtype='int32')

## now create an obspy trace
## we could load the stationxml and get the metadata from there
## but that's a different tutorial
## for now let's do it by hand
#trace = Trace()
#trace.stats.network = 'XX'
#trace.stats.station = '12345'
#trace.stats.location = '01'
#trace.stats.channel = 'DPZ'
#trace.stats.starttime = UTCDateTime('2019-03-14T05:00:00.000000Z')
#trace.stats.sampling_rate = 250.0
#trace.data = data
#
# now we have our data let's set up PH5
# open ph5 for editing
#path = '.'
#ph5_object = experiment.ExperimentGroup(
#    nickname='master.ph5',
#    currentpath=path)
#ph5_object.ph5open(True)
#ph5_object.initgroup()


#
## lets create an obspytoph5 instance
## we want a single mini file and start at mini file 1
#obs = obspytoph5.ObspytoPH5(
#    ph5_object,
#    path,
#    num_mini=1,
#    first_mini=1)
## turn on verbose logging so we can see more info
#obs.verbose = True
## we give it a our trace and should get a message
## back saying done as well as an index table to be loaded
#message, index_t = obs.toph5((trace, 'Trace'))
#
## now load are index table
#for entry in index_t:
#    ph5_object.ph5_g_receivers.populateIndex_t(entry)
#
## the last thing we need ot do ater loading
## all our data is to update external refeerences
## this takes all the mini files and adds their
## references to the master so we can find the data
#obs.update_external_references(index_t)
#
## be nice and close the file
#ph5_object.ph5close()