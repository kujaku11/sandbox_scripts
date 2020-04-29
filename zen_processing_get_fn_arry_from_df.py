#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 11:45:51 2020

@author: peacock
"""

import pandas as pd
from pathlib import Path

fn = r"/mnt/hgfs/MT/MNP2019/mnp172/processing_df.csv"
header_len = 23

tol_dict = {4096: {'s_diff': 5 * 60 * 4096,
                   'min_points': 2**18},
            256: {'s_diff': 3 * 3600 * 256,
                  'min_points': 2**19},
            4: {'s_diff': 3 * 3600 * 4,
                'min_points': 2**14}}

df = pd.read_csv(fn)
df.start = pd.to_datetime(df.start, errors='coerce')
df.stop = pd.to_datetime(df.stop, errors='coerce')
df.remote = df.remote.astype(str)
df.cal_fn = df.cal_fn.astype(str)

def make_block_entry(entry, nskip, nread, rr_num=1):
    """

    :param entry: DESCRIPTION
    :type entry: TYPE
    :param nkip: DESCRIPTION
    :type nkip: TYPE
    :param nread: DESCRIPTION
    :type nread: TYPE
    :param rr_num: DESCRIPTION, defaults to 1
    :type rr_num: TYPE, optional
    :return: DESCRIPTION
    :rtype: TYPE

    """

    r_dict = dict([('fn', entry.fn_ascii),
                   ('nread', nread),
                   ('nskip', nskip),
                   ('comp', entry.component),
                   ('calibration_fn', entry.cal_fn),
                   ('rr', entry.remote),
                   ('rr_num', rr_num),
                   ('start', entry.start),
                   ('stop', entry.stop),
                   ('sampling_rate', entry.sampling_rate),
                   ('station', entry.station)])
    return r_dict


def compare_times(entry, start, stop, header_len=23):
    """

    :param entry_01: DESCRIPTION
    :type entry_01: TYPE
    :param entry_02: DESCRIPTION
    :type entry_02: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """

    sr = entry.sampling_rate
    info_dict = {'nskip': 0, 'nread': 0, 'start_diff': 0, 'end_diff': 0}

    # estimate time difference at beginning
    start_time_diff = sr * (start - entry.start).total_seconds()
    info_dict['start_diff'] = start_time_diff
    # if difference is positive entry starts before station
    if start_time_diff > 0:
        info_dict['nskip'] = header_len + start_time_diff
        info_dict['nread'] = entry.nread - start_time_diff
    else:
        info_dict['nskip'] = header_len
        info_dict['nread'] = entry.nread

    # check the end times
    end_time_diff = sr * (entry.stop - stop).total_seconds()
    info_dict['end_diff'] = end_time_diff
    # if end diff is positive entry ends after station
    if end_time_diff > 0:
        info_dict['nread'] -= end_time_diff

    return info_dict


def make_block_df(block_list):
    """

    :param block_list: DESCRIPTION
    :type block_list: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """

    block_df = pd.DataFrame(block_list)
    block_df = block_df.infer_objects()
    block_df.start = pd.to_datetime(block_df.start)
    block_df.stop = pd.to_datetime(block_df.stop)

    return block_df


def align_block(block_df):
    """

    :param block_df: DESCRIPTION
    :type block_df: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """

    b_start = block_df.start.max()
    b_stop = block_df.stop.min()

    for entry in block_df.itertuples():
        diff_dict = compare_times(entry, b_start, b_stop)
        for key in ['nskip', 'nread']:
            block_df.at[entry.Index, key] = diff_dict[key]

    block_df.nread = block_df.nread.min()
    return block_df

def sort_blocks(df):
    """

    :param station_df: DESCRIPTION
    :type station_df: TYPE
    :param remote_df: DESCRIPTION
    :type remote_df: TYPE
    :return: DESCRIPTION
    :rtype: TYPE

    """

    birrp_dict = {}
    for sr in df.sampling_rate.unique():
        sr_list = []
        sr_df = df[(df.sampling_rate == sr) & (df.remote == 'False')]
        rr_df = df[(df.sampling_rate == sr) & (df.remote == 'True')]
        rr_stations = dict([(rr, ii) for ii, rr in
                            enumerate(rr_df.station.unique())])

        # sort through station blocks first
        for block in sr_df.block.unique():
            block_list = []
            block_df = sr_df[sr_df.block == block]
            # find the latest start time
            start = block_df.start.max()
            stop = block_df.stop.min()
            if str(stop) == 'NaT':
                print('Warning: Skipping block {0} for {1}.  '.format(block, sr) +\
                      'Reason: no end time')
                continue

            # get information for station block and align
            for entry in block_df.itertuples():
                block_list.append(make_block_entry(entry, 0, entry.n_samples))

            # make the block into a dataframe
            block_birrp_df = make_block_df(block_list)

            # --> get remote reference blocks
            # check for start time
            rr_block_list = []
            for rr_entry in rr_df.itertuples():
                if rr_entry.start > stop:
                    continue
                t_diff = abs((rr_entry.start - start).total_seconds()) * sr
                # check to see if the difference is within given tolerance
                if t_diff < tol_dict[sr]['s_diff']:
                    # check number of samples
                    rr_samples = rr_entry.n_samples - t_diff
                    if rr_samples < tol_dict[sr]['min_points']:
                        print('WARNING: skipping {0} block {1} df {2} at {3}'.format(
                              rr_entry.station, rr_entry.block,
                              rr_entry.sampling_rate,
                              rr_entry.start) +
                              '\n\tNot enough points {0}'.format(rr_samples))
                    # make a block entry and append
                    else:
                        rr_block_list.append(make_block_entry(rr_entry,
                                             0,
                                             rr_entry.n_samples,
                                             rr_stations[rr_entry.station]))

            # check to make sure there are remote references
            if len(rr_block_list) > 1:
                rr_block_birrp_df = make_block_df(rr_block_list)
                block_birrp_df = block_birrp_df.append(rr_block_birrp_df)

            # align block and append
            sr_list.append(align_block(block_birrp_df.reset_index()))
        birrp_dict[sr] = sr_list

    return birrp_dict
# =============================================================================
# Test
# =============================================================================
birrp_blocks_dict = sort_blocks(df)
