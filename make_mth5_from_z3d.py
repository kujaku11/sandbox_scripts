# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 12:24:48 2022

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
from mth5.io.zen import Z3DCollection
from mth5.mth5 import MTH5
from mth5 import read_file

from mt_metadata.utils.mttime import MTime, get_now_utc

# =============================================================================
z3d_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\mt\cl2022")
zc = Z3DCollection(z3d_path)
runs = zc.get_runs(sample_rates=[256, 4096])
stem = "cl"

st = MTime(get_now_utc())
m = MTH5()
m.open_mth5(zc.file_path.joinpath("cl2022.h5"))

survey_group = m.add_survey("cl2022")

for station_id in runs.keys():
    st_time = MTime(get_now_utc())
    station_name = f"{stem}{station_id}"
    print(f"Loading Station {station_name}: {(st_time - st):.2f} seconds")
    station_group = survey_group.stations_group.add_station(station_name)
    station_group.metadata.update(zc.station_metadata_dict[station_id])
    station_group.metadata.id = station_name
    station_group.write_metadata()
    for run_id, run_df in runs[station_id].items():
        run_time = MTime(get_now_utc())
        print(f"\tLoading Run {run_id}: {(run_time - st_time):.2f} seconds")
        run_group = station_group.add_run(run_id)
        for row in run_df.itertuples():
            ch_ts = read_file(row.fn)
            run_group.from_channel_ts(ch_ts)

        run_group.update_run_metadata()

    # update station metadata from all the new runs
    station_group.update_station_metadata()

# update survey metadata from added stations
survey_group.update_survey_metadata()

# m.close_mth5()
et = MTime(get_now_utc())

print(f"Took {(et - st):.2f} seconds")
