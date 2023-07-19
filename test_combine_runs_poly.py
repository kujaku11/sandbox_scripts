# -*- coding: utf-8 -*-
"""
Created on Wed May 24 13:09:14 2023

@author: jpeacock
"""
# =============================================================================
# Imports
# =============================================================================
from pathlib import Path

from mth5 import read_file
from mth5.io.zen import Z3DCollection, zen_tools
from mth5.timeseries import RunTS

# =============================================================================
station = "gz316"
save_path = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\GZ2023").joinpath(
    station
)

zc = Z3DCollection(save_path)
runs = zc.get_runs(sample_rates=[4096, 1024, 256])

for station_id in runs.keys():
    run_list = []
    for run_id, run_df in runs[station_id].items():
        ch_list = []
        for row in run_df.itertuples():
            ch_ts = read_file(
                row.fn,
                calibration_fn=r"c:\Users\jpeacock\OneDrive - DOI\MTData\antenna_20190411.cal",
            )

            ch_list.append(ch_ts)
        run_list.append(RunTS(ch_list))

    combined_run = run_list[0].merge(
        run_list[1:], new_sample_rate=1, resample_method="poly"
    )
    combined_run.run_metadata.id = "sr1_0001"


print(combined_run.__str__())
combined_run.plot()
