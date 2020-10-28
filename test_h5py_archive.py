# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 13:48:30 2018

@author: jpeacock
"""

import mtpy.usgs.usgs_archive as archive
import h5py
import numpy as np
import os
import datetime

st = datetime.datetime.now()
z3d_path = r"d:\Peacock\MTData\GabbsValley\gv01"


zc = archive.Z3DCollection()
fn_list = zc.get_time_blocks(z3d_path)


h5_fn = r"d:\Peacock\MTData\GabbsValley\gv01\h5_test.hdf5"

if os.path.exists(h5_fn):
    os.remove(h5_fn)


h5_obj = h5py.File(h5_fn, "w")
for ii, fn_block in enumerate(fn_list, 1):
    ts_db, meta_arr = zc.merge_ts(fn_list[0])
    # fill attributes
    h5_obj.attrs["datum"] = "WGS84"
    h5_obj.attrs["latitude"] = meta_arr["lat"].mean()
    h5_obj.attrs["longitude"] = meta_arr["lon"].mean()
    h5_obj.attrs["elevation"] = archive.get_nm_elev(
        meta_arr["lat"].mean(), meta_arr["lon"].mean()
    )
    h5_obj.attrs["station"] = "gv01"
    # fill channel attributes
    for m_arr in meta_arr:
        for c_attr, h_attr in zip(
            ["ch_num", "ch_length", "ch_azm"], ["sensor", "length", "azimuth"]
        ):
            h5_obj.attrs["{0}_{1}".format(m_arr["comp"].lower(), h_attr)] = m_arr[
                c_attr
            ]

    # create group for schedule action
    schedule = h5_obj.create_group("schedule_{0:02}".format(ii))
    # add metadata
    schedule.attrs["start_time"] = meta_arr["start"].max()
    schedule.attrs["stop_time"] = meta_arr["stop"].min()
    schedule.attrs["n_samples"] = meta_arr["n_samples"].min()
    schedule.attrs["n_channels"] = meta_arr.size
    schedule.attrs["sampling_rate"] = meta_arr["df"].mean()

    ### add datasets for each channel
    for comp in ts_db.columns:
        d_set = schedule.create_dataset(
            comp, data=ts_db[comp], compression="gzip", compression_opts=4
        )
    #    m_arr = meta_arr[np.where(meta_arr['comp'] == comp)][0]
    #    for d_attr in ['ch_length', 'ch_num', 'ch_azm']:
    #        d_set.attrs[d_attr] = m_arr[d_attr]

h5_obj.close()

et = datetime.datetime.now()

t_diff = et - st

print("Took --> {0:.2f} seconds".format(t_diff.total_seconds()))
