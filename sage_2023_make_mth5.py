# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# =============================================================================
from pathlib import Path
from mth5.mth5 import MTH5
from mth5 import read_file
from mth5.io.phoenix import ReceiverMetadataJSON, PhoenixCollection

# =============================================================================

station_dir = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2023\102_060923"
)

phx_collection = PhoenixCollection(file_path=station_dir)
run_dict = phx_collection.get_runs(sample_rates=[150, 24000])

with MTH5() as m:
    m.open_mth5(station_dir.joinpath("mth5_from_phoenix.h5"), "w")
    survey_metadata = phx_collection.metadata_dict["102"].survey_metadata
    survey_group = m.add_survey(survey_metadata.id)
    for station_id, station_dict in run_dict.items():
        station_metadata = phx_collection.metadata_dict["102"].station_metadata
        station_group = survey_group.stations_group.add_station(
            station_metadata.id, station_metadata=station_metadata
        )
        for run_id, run_df in station_dict.items():
            run_metadata = phx_collection.metadata_dict["102"].run_metadata
            run_metadata.id = run_id
            run_metadata.sample_rate = float(run_df.sample_rate.unique()[0])

            run_group = station_group.add_run(
                run_metadata.id, run_metadata=run_metadata
            )
            for row in run_df.itertuples():
                ch_ts = read_file(
                    row.fn,
                    **{
                        "channel_map": phx_collection.metadata_dict[
                            "102"
                        ].channel_map
                    }
                )
                ch_metadata = phx_collection.metadata_dict[
                    "102"
                ].get_ch_metadata(ch_ts.channel_metadata.channel_number)
                # need to update the time period and sample rate as estimated from the data not the metadata
                ch_metadata.sample_rate = ch_ts.sample_rate
                ch_metadata.time_period.update(
                    ch_ts.channel_metadata.time_period
                )
                ch_ts.channel_metadata.update(ch_metadata)

                # add channel to the run group
                ch_dataset = run_group.from_channel_ts(ch_ts)

            run_group.update_run_metadata()

    station_group.update_station_metadata()
    station_group.write_metadata()

    survey_group.update_survey_metadata()
    survey_group.write_metadata()

    m.channel_summary.summarize()
