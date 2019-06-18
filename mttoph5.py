"""
Put MT time series into PH5 format following the example from Obspy written
by Derick Hess

Using mtpy package to read in MT time series in Z3D format, but could extend
that to any type of time series later.

J. Peacock
June-2019
"""
import logging
import os
import re
import glob
from ph5.core import experiment
from mtpy.core import ts as mtts
from mtpy.usgs import zen

PROG_VERSION = '2019.65'
LOGGER = logging.getLogger(__name__)


class MTtoPH5Error(Exception):
    """
    Exception raised when there is a problem with the request.
    :param: message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

class MTtoPH5(object):
    """
    Load in MT time series to PH5 format.  
    
    Currently can read in Z3D or ascii files and gets metadata from those files  
    
    :param ph5_object: Main PH5 object to add files to
    :type ph5_object: PH5.core.experiment
    
    :param ph5_path: full path to PH5 file minus the extension
    :type ph5_path: string
    
    :param num_mini: number of mini files to make
    :type num_mini: int
    
    :param first_mini: number of first mini file
    :type first_mini: int
    
    .. note:: For now the organization is:
              * Experiment
                  - MT station 01 
                      * Schedule or Run 01
                          - EX, EY, HX, HY, HZ
                      * Schedule or Run 02
                          - EX, EY, HX, HY, HZ
                  - MT station 01 
                      * Schedule or Run 01
                          - EX, EY, HX, HY, HZ
                      * Schedule or Run 02
                          - EX, EY, HX, HY, HZ
                          
    :Example: ::
        
        >>> ph5_fn = r"./test_ph5.ph5"
        >>> fn_list = glob.glob(r"/home/mt_files/*.Z3D")
        >>> ### initialize a PH5 object
        >>> ph5_obj = experiment.ExperimentGroup(nickname='test_ph5',
        >>> ...                           currentpath=os.path.dirname(ph5_fn))
        >>> ph5_obj.ph5open(True)
        >>> ph5_obj.initgroup()
        >>> ### initialize mt_to_ph5 object want only 1 mini file starting at 1
        >>> mt_obj = MTtoPH5(ph5_obj, os.path.dirname(ph5_fn), 1, 1)
        >>> # turn on verbose logging so we can see more info
        >>> mt_obj.verbose = True
        >>> # only do the first 5 files because that is one schedule or run
        >>> message, index_t = mt_obj.to_ph5(fn_list[0:5])
        >>> # now load are index table
        >>> for entry in index_t:
        >>>     ph5_obj.ph5_g_receivers.populateIndex_t(entry)
        >>> 
        >>> # the last thing we need ot do ater loading
        >>> # all our data is to update external refeerences
        >>> # this takes all the mini files and adds their
        >>> # references to the master so we can find the data
        >>> mt_obj.update_external_references(index_t)
        >>>  
        >>> # be nice and close the file
        >>> ph5_obj.ph5close()                   
    """
    

    def __init__(self, ph5_object,
                 ph5_path,
                 num_mini=None,
                 first_mini=None):
        """
        :param ph5_object: Main PH5 object to add files to
        :type ph5_object: PH5.core.experiment
        
        :param ph5_path: full path to PH5 file minus the extension
        :type ph5_path: string
        
        :param num_mini: number of mini files to make
        :type num_mini: int
        
        :param first_mini: number of first mini file
        :type first_mini: int
        """
        self.ph5 = ph5_object
        self.ph5_path = ph5_path
        self.num_mini = num_mini
        self.first_mini = first_mini
        self.mini_size_max = 26843545600
        self.verbose = False
        self.array_names = self.ph5.ph5_g_sorts.names()
        self.arrays = list()
        for name in self.array_names:
            array_, blah = self.ph5.ph5_g_sorts.read_arrays(name)
            for entry in array_:
                self.arrays.append(entry)
        self.time_t = list()

    def open_mini(self, mini_num):
        """
        Open PH5 file, miniPH5_xxxxx.ph5
        :type: str
        :param mini_num: name of mini file to open
        :return class: ph5.core.experiment, str: name
        """

        mini_num = str(mini_num).zfill(5)
        filename = "miniPH5_{0}.ph5".format(mini_num)
        print('--- mini filename = {0}'.format(filename))
        print('    {0}'.format(self.ph5_path))
        exrec = experiment.ExperimentGroup(nickname=filename,
                                           currentpath=self.ph5_path)
        exrec.ph5open(True)
        exrec.initgroup()
        return exrec, filename

    def get_minis(self, directory):
        """
        takes a directory and returns a list of all mini files
        in the current directory

        :type str
        :param dir
        :return: list of mini files
        """
        miniPH5RE = re.compile(r".*miniPH5_(\d+)\.ph5")
        minis = list()
        try:
            for entry in os.listdir(directory):
                # Create full path
                fullPath = os.path.join(directory, entry)
                if miniPH5RE.match(entry):
                    minis.append(fullPath)
            return minis
        except NotADirectoryError:
            print('Found no minis files in PH5 file')
            return None
        
    def get_size_mini(self, mini_num):
        """
        :param mini_num: str
        :return: size of mini file in bytes
        """
        
        filename = "miniPH5_{0:05}.ph5".format(mini_num)
        return os.path.getsize(filename)

    def get_das_station_map(self):
        """
        Checks if array tables exist
        returns None
        otherwise returns a list of dictionaries
        containing das serial numbers and stations
        :return: list
        """
        array_names = self.ph5.ph5_g_sorts.namesArray_t()
        if not array_names:
            return None
        tmp = list()
        # use tables where to search array tables and find matches
        for _array in array_names:
            tbl = self.ph5.ph5.get_node('/Experiment_g/Sorts_g/{0}'.format(
                _array))
            data = tbl.read()
            for row in data:
                tmp.append({'serial': row[4][0], 'station': row[13]})
        das_station_map = list()
        for i in tmp:
            if i not in das_station_map:
                das_station_map.append(i)
        tbl = None

        return das_station_map

    def mini_map(self, existing_minis):
        """
        :type list
        :param existing_minis: A list of mini_files with path
        :return:  list of tuples containing
        what mini file contains what serial #s
        """
        if existing_minis is None:
            return None
        mini_map = list()
        for mini in existing_minis:
            mini_num = int(mini.split('.')[-2].split('_')[-1])
            exrec = experiment.ExperimentGroup(nickname=mini)
            exrec.ph5open(True)
            exrec.initgroup()
            all_das = exrec.ph5_g_receivers.alldas_g()
            das_list = list()
            for g in all_das:
                name = g.split('_')[-1]
                das_list.append(name)
            mini_map.append((mini_num, das_list))
            exrec.ph5close()
        return mini_map
    
    def make_index_t_entry(self, ts_obj):
        """
        make a time index dictionry (index_t_entry) for a given time series.
        
        :param ts_obj: MTTS time-series object
        :returns: dictionary of necessary values
        """
        index_t_entry = {}
        # start time
        index_t_entry['start_time/ascii_s'] = (ts_obj.start_time_utc)
        index_t_entry['start_time/epoch_l'] = (ts_obj.start_time_epoch_sec)
        index_t_entry['start_time/micro_seconds_i'] = (ts_obj._start_time_struct.microsecond)
        index_t_entry['start_time/type_s'] = 'BOTH'
        
        # end time
        index_t_entry['end_time/ascii_s'] = (ts_obj.stop_time_utc)
        index_t_entry['end_time/epoch_l'] = (ts_obj.stop_time_epoch_sec)
        index_t_entry['end_time/micro_seconds_i'] = (ts_obj.ts.index[-1].microsecond)
        index_t_entry['end_time/type_s'] = 'BOTH'
        
        # time stamp -- when data was entered?
        time_stamp_utc = mtts.datetime.datetime.utcnow()
        index_t_entry['time_stamp/ascii_s'] = (time_stamp_utc.isoformat())
        index_t_entry['time_stamp/epoch_l'] = (ts_obj._convert_dt_to_sec(time_stamp_utc))
        index_t_entry['time_stamp/micro_seconds_i'] = (time_stamp_utc.microsecond)
        index_t_entry['time_stamp/type_s'] = 'BOTH'
        
        index_t_entry['serial_number_s'] = ts_obj.station
        index_t_entry['external_file_name_s'] = ''
#        index_t_entry['component_s'] = ts_obj.component.upper()
#        index_t_entry['dipole_length_f'] = ts_obj.dipole_length
#        index_t_entry['dipole_length_units_s'] = 'meters'
#        index_t_entry['sensor_id_s'] = ts_obj.chn_num
        
        return index_t_entry
    
    def make_receiver_t_entry(self, ts_obj):
        """
        make receiver table entry
        """
        
        receiver_t_entry = {}
        receiver_t_entry['orientation/azimuth/value_f'] = ts_obj.azimuth
        receiver_t_entry['orientation/azimuth/units_s'] = 'degrees'
        receiver_t_entry['orientation/dip/value_f'] = 0
        receiver_t_entry['orientation/dip/units_s'] = 'degrees'
        receiver_t_entry['orientation/description_s'] = ts_obj.component
        receiver_t_entry['orientation/channel_number_i'] = ts_obj.chn_num
        
        return receiver_t_entry
        
    def make_das_entry(self, ts_obj):
        """
        Make a metadata array for a given mtts object
        
        :param ts_obj: MTTS object
        :return: dictionary of das information
        """
        das = {}
        # start time information
        das['time/ascii_s'] = ts_obj.start_time_utc
        das['time/epoch_l'] = ts_obj.start_time_epoch_sec
        das['time/micro_seconds_i'] = ts_obj._start_time_struct.microsecond
        das['time/type_s'] = 'BOTH'
        
        das['sample_rate_i'] = ts_obj.sampling_rate
        das['sample_rate_multiplier_i'] = 1
        
        das['channel_number_i'] = ts_obj.component
        das['sample_count_i'] = ts_obj.n_samples
        das['raw_file_name_s'] = ts_obj.fn
#        das['component_s'] = ts_obj.component.upper()
#        das['dipole_length_f'] = ts_obj.dipole_length
#        das['dipole_length_units_s'] = 'meters'
#        das['sensor_id_s'] = ts_obj.chn_num
#        das['array_name_data_a'] = '{0}_{1}_{2}'.format('Data',
#                                                        ts_obj.component,
#                                                        '1')
        
        return das
    
    def load_ts_obj(self, ts_fn):
        """
        load an MT file
        """
        if isinstance(ts_fn, str):
            if ts_fn.lower().endswith('.z3d'):
                z3d_obj = zen.Zen3D(ts_fn)
                z3d_obj.read_z3d()
                ts_obj = z3d_obj.ts_obj
            elif ts_fn[-2:].lower() in ['ex', 'ey', 'hx', 'hy', 'hz']:
                ts_obj = mtts.MTTS()
                ts_obj.read_file(ts_fn)
        elif isinstance(ts_fn, mtts.MTTS):
            ts_obj = ts_fn
        else:
            raise mtts.MTTSError("Do not understand {0}".format(type(ts_fn)))
            
        return ts_obj
    
    def get_current_mini(self, ts_obj):
        """
        get the current mini file
        """
        ### check for existing files in PH5 file
        existing_minis = self.get_minis(self.ph5_path)

        # gets mapping of whats dases each minifile contains
        minis = self.mini_map(existing_minis)
        
        if not existing_minis:
            current_mini = self.first_mini
        else:
            current_mini = None
            for mini in minis:
                if ts_obj.station in mini[1]:
                    current_mini = mini[0]
                    break
            ### get the largest file?
            if not current_mini:
                largest = 0
                for x in minis:
                    if x[0] >= largest:
                        largest = x[0]
                if (self.get_size_mini(largest) <
                        self.mini_size_max):
                    current_mini = largest
                else:
                    current_mini = largest + 1
                        
        return current_mini

    def to_ph5(self, ts_list):
        """
        Takes a list of either files or MTTS objects and puts them into a 
        PH5 file.
        
        :param ts_list: list of filenames (full path) or ts objects
        :returns: success message
        """
        index_t = list()

        # check if we are opening a file or mt ts object
        for count, fn in enumerate(ts_list, 1):
            ts_obj = self.load_ts_obj(fn)
            
            ### start populating das table and data arrays
            index_t_entry = self.make_index_t_entry(ts_obj)
            das_t_entry = self.make_das_entry(ts_obj)
            receiver_t_entry = self.make_receiver_t_entry(ts_obj)
            
            ### get the current mini file
            current_mini = self.get_current_mini(ts_obj)
            mini_handle, mini_name = self.open_mini(current_mini)
            
            # get node reference or create new node
            d = mini_handle.ph5_g_receivers.getdas_g(ts_obj.station)
            if not d:
                d, t, r, ti = mini_handle.ph5_g_receivers.newdas(ts_obj.station)
            
            ### make name for array data going into mini file
            while True:
                next_ = '{0:05}'.format(count)
                das_t_entry['array_name_data_a'] = "Data_a_{0}".format(next_)
                node = mini_handle.ph5_g_receivers.find_trace_ref(das_t_entry['array_name_data_a'])
                if not node:
                    break
                count = count + 1
                continue
            
            ### make a new array
            mini_handle.ph5_g_receivers.setcurrent(d)
            mini_handle.ph5_g_receivers.newarray(das_t_entry['array_name_data_a'],
                                                 ts_obj.ts.data,
                                                 dtype=ts_obj.ts.data.dtype,
                                                 description=None)
            
            ### create external file names
            index_t_entry['external_file_name_s'] = "./{}".format(mini_name)
            das_path = "/Experiment_g/Receivers_g/Das_g_{0}".format(ts_obj.station)
            index_t_entry['hdf5_path_s'] = das_path
            
            ### populate metadata tables
            mini_handle.ph5_g_receivers.populateDas_t(das_t_entry)
            mini_handle.ph5_g_receivers.populateIndex_t(index_t_entry)
            mini_handle.ph5_g_receivers.populateReceiver_t(receiver_t_entry)
            #mini_handle.ph5_g_receivers.populateTime_t_()

            index_t.append(index_t_entry)
            # Don't forget to close minifile
            mini_handle.ph5close()
        #LOGGER.info('Finished processing {0}'.format(ts_obj.fn))

        # last thing is to return the index table so far.
        # index_t will be populated in main() after all
        # files are loaded
        return "done", index_t

    def update_external_references(self, index_t):
        """
        looks through index_t and updates master.ph5
        with external references to das group in mini files
        :type list
        :param index_t:
        :return:
        """
        n = 0
        #LOGGER.info("updating external references")
        for i in index_t:
            external_file = i['external_file_name_s'][2:]
            external_path = i['hdf5_path_s']
            target = external_file + ':' + external_path
            external_group = external_path.split('/')[3]

            try:
                group_node = self.ph5.ph5.get_node(external_path)
                group_node.remove()

            except Exception as e:
                print(e)
                pass

            #   Re-create node
            try:
                self.ph5.ph5.create_external_link(
                    '/Experiment_g/Receivers_g', external_group, target)
                n += 1
            except Exception as e:
                # pass
                print(e)
                #LOGGER.error(e.message)

        return

# =============================================================================
# Test
# =============================================================================
#ts_fn = r"c:\Users\jpeacock\Documents\GitHub\sandbox\ts_test.EX"
ph5_fn = r"c:\Users\jpeacock\Documents\GitHub\sandbox\test_ph5.ph5"

fn_list = glob.glob(r"c:\Users\jpeacock\Documents\imush\O015\*.Z3D")

### initialize a PH5 object
ph5_obj = experiment.ExperimentGroup(nickname='test_ph5',
                                     currentpath=os.path.dirname(ph5_fn))
ph5_obj.ph5open(True)
ph5_obj.initgroup()

### initialize mt2ph5 object
mt_obj = MTtoPH5(ph5_obj, os.path.dirname(ph5_fn), 1, 1)
# turn on verbose logging so we can see more info
mt_obj.verbose = True
# we give it a our trace and should get a message
# back saying done as well as an index table to be loaded
message, index_t = mt_obj.to_ph5(fn_list[0:5])

# now load are index table
for entry in index_t:
    ph5_obj.ph5_g_receivers.populateIndex_t(entry)

# the last thing we need ot do ater loading
# all our data is to update external refeerences
# this takes all the mini files and adds their
# references to the master so we can find the data
mt_obj.update_external_references(index_t)

# be nice and close the file
ph5_obj.ph5close()
