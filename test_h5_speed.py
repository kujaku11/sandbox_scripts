# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 10:19:11 2021

:copyright: 
    Jared Peacock (jpeacock@usgs.gov)

:license: MIT

"""
from mt_metadata.utils.mttime import MTime, get_now_utc
from mth5.io import zen
from mth5 import mth5
import h5py
from pathlib import Path

h5 = False
fn = Path(r"c:\Users\jpeacock\load_test.h5")
if fn.exists():
    fn.unlink()

if h5:
    m = h5py.File(fn, mode="w")

    g = m.create_group("gv112")

    r = g.create_group("001")

    ch = zen.Z3D(
        r"c:\Users\jpeacock\Documents\test_data\gv116\gv116_20200819_231518_256_HY.Z3D"
    )
    ch.read_z3d()
    ch_ts = ch.to_channelts()

    st = MTime(get_now_utc())

    d = r.create_dataset(
        "hx",
        # shape=ch_ts.ts.shape,
        dtype="int32",
        data=ch_ts.ts,
        shuffle=None,
        fletcher32=None,
        compression=None,
        compression_opts=None,
        chunks=True,
        maxshape=(None,),
    )

    d.attrs.update(ch_ts.channel_metadata.to_dict(single=True))

    et = MTime(get_now_utc())

    print(f"Took: {et - st}")

    m.flush()
    m.close()

if not h5:
    m = mth5.MTH5()
    m.open_mth5(fn, mode="w")

    g = m.add_station("gv112")

    r = g.add_run("001")

    ch = zen.Z3D(
        r"c:\Users\jpeacock\Documents\test_data\gv116\gv116_20200819_231518_256_HY.Z3D"
    )
    ch.read_z3d()
    ch_ts = ch.to_channelts()

    st = MTime(get_now_utc())
    for cc in ["ex", "ey", "hx", "hy", "hz"]:
        chg = r.add_channel(
            cc,
            "magnetic",
            ch_ts.ts,
            channel_dtype="int32",
            channel_metadata=ch_ts.channel_metadata,
            return_ch=True,
            shuffle=None,
            fletcher32=None,
            compression=None,
            compression_opts=None,
            chunks=True,
            maxshape=(None,),
        )

    et = MTime(get_now_utc())

    print(f"Took: {et - st}")

    m.close_mth5()
