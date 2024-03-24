# -*- coding: utf-8 -*-
"""

Created on Tue Jul 25 16:14:30 2023

:author: Jared Peacock

:license: MIT

"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path

from mth5 import read_file
from mth5.io.zen import Z3DCollection
from mth5.mth5 import MTH5

# =============================================================================

survey_id = "ST2024"
survey_dir = Path(r"c:\MT").joinpath(survey_id)
save_dir = survey_dir.joinpath("mth5")
cal_file = Path(r"c:\MT\antenna.cal")

save_dir.mkdir(exist_ok=True)

# loop over stations
for station in ["st2024", "st2025", "st3026"]:
    station_path = survey_dir.joinpath(station)
    mth5_path = save_dir.joinpath(f"{station}_with_1s_run.h5")
    combine = True

    zc = Z3DCollection(station_path)
    runs = zc.get_runs(sample_rates=[4096, 1024, 256])

    zen_station = list(runs.keys())[0]

    with MTH5() as m:
        m.open_mth5(mth5_path)
        survey_group = m.add_survey(survey_id)
        for station_id in runs.keys():
            station_group = survey_group.stations_group.add_station(
                station_id
            )
            station_group.metadata.update(
                zc.station_metadata_dict[station_id]
            )
            station_group.write_metadata()
            if combine:
                run_list = []
            for run_id, run_df in runs[station_id].items():
                run_group = station_group.add_run(run_id)
                for row in run_df.itertuples():
                    ch_ts = read_file(
                        row.fn,
                        calibration_fn=cal_file,
                    )
                    run_group.from_channel_ts(ch_ts)
                run_group.update_metadata()
                if combine:
                    run_list.append(run_group.to_runts())
            if combine:
                # Combine runs and down sample to 1 second.
                combined_run = run_list[0].merge(
                    run_list[1:], new_sample_rate=1
                )
                combined_run.run_metadata.id = "sr1_0001"
                combined_run_group = station_group.add_run("sr1_0001")
                combined_run_group.from_runts(combined_run)
                combined_run_group.update_metadata()
            station_group.update_metadata()
        survey_group.update_metadata()
        print("=" * 50)
        print("=" * 50)
