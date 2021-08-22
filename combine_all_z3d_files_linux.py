# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 10:08:23 2020

@author: jpeacock
"""

from mtpy.usgs import zen
from mtpy.core import ts
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


def get_z3d_info(z3d_path):
    """
    get information on z3d files
    """
    if not isinstance(z3d_path, Path):
        z3d_path = Path(z3d_path)
    # need to get all the files for one channel
    fn_dict = dict([(key, []) for key in ['ex', 'ey', 'hx', 'hy', 'hz']])
    # get all z3d files within a given folder, will look through recursively
    fn_list = [fn_path for fn_path in z3d_path.rglob('*')
               if fn_path.suffix in ['.z3d', '.Z3D']]
    # loop over files, read just the metadata and get important information
    for fn in fn_list:
        z_obj = zen.Zen3D(fn)
        z_obj.read_all_info()
        fn_dict[z_obj.component].append({'start': z_obj.zen_schedule.isoformat(),
                                         'df': z_obj.df,
                                         'fn': z_obj.fn})

    return fn_dict

def combine_z3d_files(z3d_path, new_sampling_rate=4, t_buffer=8*3600,
                      comp_list=['ex', 'ey', 'hx', 'hy', 'hz']):
    """
    Combine all z3d files for a given station and given component for 
    processing and getting the long period estimations.

    :param str z3d_path: full path to z3d files
    :param str component: component to combine
    :param int new_sampling_rate: new sampling rate of the data
    :param int t_buffer: buffer for the last time series, should be length
                         of longest schedule chunk
    """
    st = datetime.datetime.now()
    attr_list = [
        "station",
        "channel_number",
        "component",
        "coordinate_system",
        "dipole_length",
        "azimuth",
        "units",
        "lat",
        "lon",
        "elev",
        "datum",
        "data_logger",
        "instrument_id",
        "calibration_fn",
        "declination",
        "fn",
        "conversion",
        "gain",
    ]

    fn_df = get_z3d_info(z3d_path)

    return_fn_list = []
    for comp in comp_list:
        if len(fn_df[comp]) == 0:
            print(
                'Warning: Skipping {0} because no Z3D files found.'.format(comp))
            continue
        comp_df = pd.DataFrame(fn_df[comp])
        # sort the data frame by date
        comp_df = comp_df.sort_values('start')

        # get start date and end at last start date, get time difference
        start_dt = datetime.datetime.fromisoformat(comp_df.start.min())
        end_dt = datetime.datetime.fromisoformat(comp_df.start.max())
        t_diff = (end_dt - start_dt).total_seconds()

        ### make a new MTTS object that will have a length that is buffered
        ### at the end to make sure there is room for the data, will trimmed
        new_ts = ts.MTTS()
        new_ts.ts = np.zeros(int((t_diff + t_buffer) * sampling_rate))
        new_ts.sampling_rate = sampling_rate
        new_ts.start_time_utc = start_dt

        # make an attribute dictionary that can be used to fill in the new
        # MTTS object
        attr_dict = dict([(key, []) for key in attr_list])
        # loop over each z3d file for the given component

        for row in comp_df.itertuples():
            z_obj = zen.Zen3D(row.fn)
            print(row.fn)
            z_obj.read_z3d()
            t_obj = z_obj.ts_obj
            # decimate to the required sampling rate
            t_obj.decimate(int(z_obj.df/sampling_rate))
            # fill the new time series with the data at the appropriate times
            print(f"start = {t_obj.ts.index[0]}, end = {t_obj.ts.index[-1]}")
            new_ts.ts.data[(new_ts.ts.index >= t_obj.ts.index[0]) &
                           (new_ts.ts.index <= t_obj.ts.index[-1])] = t_obj.ts.data
            

            # get the end date as the last z3d file
            end_date = z_obj.ts_obj.ts.index[-1]
            # fill attribute data frame
            for attr in attr_list:
                attr_dict[attr].append(getattr(t_obj, attr))

        # need to trim the data
        new_ts.ts = new_ts.ts.data[(new_ts.ts.index >= start_dt) &
                                   (new_ts.ts.index <= end_date)].to_frame()

        # fill gaps with forwards or backwards values, this seems to work
        # better than interpolation and is faster than regression.
        # The gaps should be max 13 seconds if everything went well
        new_ts.ts.data[new_ts.ts.data == 0] = np.nan
        new_ts.ts.data.fillna(method='ffill', inplace=True)

        # fill the new MTTS with the appropriate metadata
        attr_df = pd.DataFrame(attr_dict)
        for attr in attr_list:
            try:
                attr_series = attr_df[attr][attr_df[attr] != 0]
                try:
                    setattr(new_ts, attr, attr_series.median())
                except TypeError:
                    setattr(new_ts, attr, attr_series.mode()[0])
            except ValueError:
                print('Warning: could not set {0}'.format(attr))

        ascii_fn = '{0}_combined_{1}.{2}'.format(new_ts.station,
                                                 int(new_ts.sampling_rate),
                                                 new_ts.component)

        sv_fn_ascii = z3d_path.joinpath(ascii_fn)
        new_ts.write_ascii_file(sv_fn_ascii.absolute())

        return_fn_list.append(sv_fn_ascii)

    et = datetime.datetime.now()
    compute_time = (et - st).total_seconds()
    print("   Combining took {0:.2f} seconds".format(compute_time))
    return return_fn_list


# =============================================================================
# test
# =============================================================================

#combined_fn_list = combine_z3d_files(fn_path, comp_list=["ex"])
z3d_path = Path(r"/mnt/hgfs/MT_Data/Katmai2021/KAT028")
sampling_rate = 4
t_buffer = 8 * 3600

attr_list = ['station', 'channel_number', 'component', 'coordinate_system',
             'dipole_length', 'azimuth', 'units', 'lat', 'lon', 'elev',
             'datum', 'data_logger', 'instrument_id', 'calibration_fn',
             'declination',  'fn', 'conversion', 'gain']

comp = "hx"

fn_df = get_z3d_info(z3d_path)

return_fn_list = []
comp_df = pd.DataFrame(fn_df[comp])
# sort the data frame by date
comp_df = comp_df.sort_values('start')

# get start date and end at last start date, get time difference
start_dt = datetime.datetime.fromisoformat(comp_df.start.min())
end_dt = datetime.datetime.fromisoformat(comp_df.start.max())
t_diff = (end_dt - start_dt).total_seconds()

# make a new MTTS object that will have a length that is buffered
# at the end to make sure there is room for the data, will trimmed
new_ts = ts.MTTS()
new_ts.ts = np.zeros(int((t_diff + t_buffer) * sampling_rate))
new_ts.sampling_rate = sampling_rate
new_ts.start_time_utc = start_dt

# make an attribute dictionary that can be used to fill in the new
# MTTS object
attr_dict = dict([(key, []) for key in attr_list])
# loop over each z3d file for the given component
index = 1
for row in comp_df.itertuples():
    z_obj = zen.Zen3D(row.fn)
    print(row)
    z_obj.read_z3d()
    t_obj = z_obj.ts_obj
    # decimate to the required sampling rate
    t_obj.decimate(int(z_obj.df/sampling_rate))
    # fill the new time series with the data at the appropriate times
    print(f"start = {t_obj.ts.index[0]}, end = {t_obj.ts.index[-1]}")
    new_ts.ts.data[(new_ts.ts.index >= t_obj.ts.index[0]) &
                   (new_ts.ts.index <= t_obj.ts.index[-1])] = t_obj.ts.data
    
    plt.figure(index)
    plt.plot(new_ts.ts)
    plt.plot(t_obj.ts)
    # get the end date as the last z3d file
    end_date = z_obj.ts_obj.ts.index[-1]
    # fill attribute data frame
    for attr in attr_list:
        attr_dict[attr].append(getattr(t_obj, attr))
        
    index += 1

# need to trim the data
new_ts.ts = new_ts.ts.data[(new_ts.ts.index >= start_dt) &
                           (new_ts.ts.index <= end_date)].to_frame()
plt.plot(new_ts.ts)

# fill gaps with forwards or backwards values, this seems to work
# better than interpolation and is faster than regression.
# The gaps should be max 13 seconds if everything went well
new_ts.ts.data[new_ts.ts.data == 0] = np.nan
new_ts.ts.data.fillna(method='ffill', inplace=True)

# fill the new MTTS with the appropriate metadata
attr_df = pd.DataFrame(attr_dict)
for attr in attr_list:
    try:
        attr_series = attr_df[attr][attr_df[attr] != 0]
        try:
            setattr(new_ts, attr, attr_series.median())
        except TypeError:
            setattr(new_ts, attr, attr_series.mode()[0])
    except ValueError:
        print('Warning: could not set {0}'.format(attr))


ascii_fn = '{0}_combined_{1}.{2}'.format(new_ts.station,
                                         int(new_ts.sampling_rate),
                                         new_ts.component)

sv_fn_ascii = z3d_path.joinpath(ascii_fn)
new_ts.write_ascii_file(sv_fn_ascii.absolute())


# et = datetime.datetime.now()
# compute_time = (et - st).total_seconds()
# print('   Combining took {0:.2f} seconds'.format(compute_time))
# return return_fn_list
# combined_fn_list = combine_z3d_files(fn_path)
