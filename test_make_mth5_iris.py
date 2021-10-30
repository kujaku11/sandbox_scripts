# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 14:42:28 2021

@author: jpeacock
"""
import pandas as pd
from mth5.clients.make_mth5 import MakeMTH5
from mt_metadata.utils.mttime import MTime, get_now_utc

ZUCAS04LQ1 = ['ZU', 'CAS04', '', 'LQE', '2020-06-02T19:00:00', '2020-07-13T19:00:00']
ZUCAS04LQ2 = ['ZU', 'CAS04', '', 'LQN', '2020-06-02T19:00:00', '2020-07-13T19:00:00']
ZUCAS04BF1 = ['ZU', 'CAS04', '', 'LFE', '2020-06-02T19:00:00', '2020-07-13T19:00:00']
ZUCAS04BF2 = ['ZU', 'CAS04', '', 'LFN', '2020-06-02T19:00:00', '2020-07-13T19:00:00']
ZUCAS04BF3 = ['ZU', 'CAS04', '', 'LFZ', '2020-06-02T19:00:00', '2020-07-13T19:00:00']
ZUNRV08LQ1 = ['ZU', 'NVR08', '', 'LQE', '2020-06-02T19:00:00', '2020-07-13T19:00:00']
ZUNRV08LQ2 = ['ZU', 'NVR08', '', 'LQN', '2020-06-02T19:00:00', '2020-07-13T19:00:00']
ZUNRV08BF1 = ['ZU', 'NVR08', '', 'LFE', '2020-06-02T19:00:00', '2020-07-13T19:00:00']
ZUNRV08BF2 = ['ZU', 'NVR08', '', 'LFN', '2020-06-02T19:00:00', '2020-07-13T19:00:00']
ZUNRV08BF3 = ['ZU', 'NVR08', '', 'LFZ', '2020-06-02T19:00:00', '2020-07-13T19:00:00']
# metadata_list = [ZUCAS04LQ1, ZUCAS04LQ2, ZUCAS04BF1, ZUCAS04BF2, ZUCAS04BF3, ZUNRV08LQ1, 
                 # ZUNRV08LQ2, ZUNRV08BF1, ZUNRV08BF2, ZUNRV08BF3]

metadata_list = [ZUCAS04LQ1, ZUCAS04LQ2, ZUCAS04BF1, ZUCAS04BF2, ZUCAS04BF3]


st = MTime(get_now_utc())
make_mth5 = MakeMTH5()
# Turn list into dataframe
metadata_df =  pd.DataFrame(metadata_list, columns=make_mth5.column_names)

# get only metadata
# station_xml, streams = make_mth5.get_inventory_from_df(metadata_df, "iris", data=False)

# df = make_mth5.get_df_from_inventory(station_xml)
mth5_file = make_mth5.make_mth5_from_fdsnclient(metadata_df, interact=True)
et = MTime(get_now_utc())

print(f"Took {et - st} seconds")