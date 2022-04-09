# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 14:42:28 2021

@author: jpeacock
"""
import pandas as pd
from mth5.clients.make_mth5 import MakeMTH5
from mt_metadata.utils.mttime import MTime, get_now_utc

EMCAY10LFE = ["EM", "CAY10", "", "LFE", "2019-10-07T00:00:00", "2019-10-30T00:00:00"]
EMCAY10LFN = ["EM", "CAY10", "", "LFN", "2019-10-07T00:00:00", "2019-10-30T00:00:00"]
EMCAY10LFZ = ["EM", "CAY10", "", "LFZ", "2019-10-07T00:00:00", "2019-10-30T00:00:00"]
EMCAY10LQE = ["EM", "CAY10", "", "LQE", "2019-10-07T00:00:00", "2019-10-30T00:00:00"]
EMCAY10LQN = ["EM", "CAY10", "", "LQN", "2019-10-07T00:00:00", "2019-10-30T00:00:00"]
ZUCAS04LQ1 = ["ZU", "CAS04", "", "LQE", "2020-06-02T19:00:00", "2020-07-13T19:00:00"]
ZUCAS04LQ2 = ["ZU", "CAS04", "", "LQN", "2020-06-02T19:00:00", "2020-07-13T19:00:00"]
ZUCAS04BF1 = ["ZU", "CAS04", "", "LFE", "2020-06-02T19:00:00", "2020-07-13T19:00:00"]
ZUCAS04BF2 = ["ZU", "CAS04", "", "LFN", "2020-06-02T19:00:00", "2020-07-13T19:00:00"]
ZUCAS04BF3 = ["ZU", "CAS04", "", "LFZ", "2020-06-02T19:00:00", "2020-07-13T19:00:00"]
ZUNRV08LQ1 = ["ZU", "NVR08", "", "LQE", "2020-06-02T19:00:00", "2020-07-13T19:00:00"]
ZUNRV08LQ2 = ["ZU", "NVR08", "", "LQN", "2020-06-02T19:00:00", "2020-07-13T19:00:00"]
ZUNRV08BF1 = ["ZU", "NVR08", "", "LFE", "2020-06-02T19:00:00", "2020-07-13T19:00:00"]
ZUNRV08BF2 = ["ZU", "NVR08", "", "LFN", "2020-06-02T19:00:00", "2020-07-13T19:00:00"]
ZUNRV08BF3 = ["ZU", "NVR08", "", "LFZ", "2020-06-02T19:00:00", "2020-07-13T19:00:00"]
request_list = [
    EMCAY10LFE,
    EMCAY10LFN,
    EMCAY10LFZ,
    EMCAY10LQE,
    EMCAY10LQN,
    ZUCAS04LQ1,
    ZUCAS04LQ2,
    ZUCAS04BF1,
    ZUCAS04BF2,
    ZUCAS04BF3,
    ZUNRV08LQ1,
    ZUNRV08LQ2,
    ZUNRV08BF1,
    ZUNRV08BF2,
    ZUNRV08BF3,
]

st = MTime(get_now_utc())
make_mth5 = MakeMTH5()
make_mth5.mth5_version = "0.2.0"
# Turn list into dataframe
metadata_df = pd.DataFrame(request_list, columns=make_mth5.column_names)

# # get only metadata
# inventory, streams = make_mth5.get_inventory_from_df(metadata_df, "iris", data=False)

# df = make_mth5.get_df_from_inventory(station_xml)
mth5_file = make_mth5.make_mth5_from_fdsnclient(metadata_df, interact=True)
et = MTime(get_now_utc())

print(f"Took {(int(et - st) // 60)}:{(et - st) % 60:05.2f} minutes")
