# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# =============================================================================
from pathlib import Path
from mth5.mth5 import MTH5
from mth5 import read_file
from mth5.io.phoenix import PhoenixCollection
from mth5.io.zen import CoilResponse

# =============================================================================

# station_dir = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2023\004_061123"
# )
# station = "004"
survey_dir = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2023")
antcal_fn = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2023\xamtant_combined_052523.cal"
)
ant_cal = CoilResponse(calibration_file=antcal_fn)

# phx_collection = PhoenixCollection(file_path=station_dir)
# run_dict = phx_collection.get_runs(sample_rates=[150, 24000])


def get_coil_numbers(comment):
    c_list = comment.split(".", 1)[-1].split()
    coil_dict = {}
    coil_keys = ["h1", "h2", "h3"]
    count = 0
    for c_str in c_list:
        c_str = c_str.replace(",", "")
        try:
            c_str = int(c_str)
            coil_dict[coil_keys[count]] = c_str
            count += 1

        except ValueError:
            pass
    return coil_dict


for station_dir in list(survey_dir.iterdir())[6:]:
    if "zen" not in station_dir.name.lower() and station_dir.is_dir():
        station = station_dir.name[0:3]
        phx_collection = PhoenixCollection(file_path=station_dir)
        run_dict = phx_collection.get_runs(sample_rates=[150, 24000])

        with MTH5() as m:
            m.open_mth5(
                station_dir.joinpath(f"vc{station}_mth5_from_phoenix.h5"), "w"
            )
            survey_metadata = phx_collection.metadata_dict[
                station
            ].survey_metadata
            survey_group = m.add_survey(survey_metadata.id)
            for station_id, station_dict in run_dict.items():
                station_metadata = phx_collection.metadata_dict[
                    station
                ].station_metadata
                station_group = survey_group.stations_group.add_station(
                    station_metadata.id, station_metadata=station_metadata
                )
                for run_id, run_df in station_dict.items():
                    run_metadata = phx_collection.metadata_dict[
                        station
                    ].run_metadata
                    run_metadata.id = run_id
                    run_metadata.sample_rate = float(
                        run_df.sample_rate.unique()[0]
                    )

                    run_group = station_group.add_run(
                        run_metadata.id, run_metadata=run_metadata
                    )
                    for row in run_df.itertuples():
                        try:
                            ch_ts = read_file(
                                row.fn,
                                **{
                                    "channel_map": phx_collection.metadata_dict[
                                        station
                                    ].channel_map,
                                    "rxcal_fn": r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2023\10621_647A2F41.rxcal.json",
                                },
                            )

                        except OSError:
                            print(
                                f"OSError: skipping {row.fn.name} likely too small"
                            )

                        if ch_ts.component in ["h1", "h2", "h3"]:
                            coil_dict = get_coil_numbers(
                                ch_ts.station_metadata.comments
                            )
                            coil_number = coil_dict[ch_ts.component]
                            coil_fap = ant_cal.get_coil_response_fap(
                                coil_number
                            )
                            ch_ts.channel_metadata.filter.name.append(
                                coil_fap.name
                            )
                            ch_ts.channel_metadata.filter.applied.append(False)
                            ch_ts.channel_response_filter.filters_list.append(
                                coil_fap
                            )

                        # add channel to the run group
                        ch_dataset = run_group.from_channel_ts(ch_ts)

                    run_group.update_run_metadata()

            station_group.update_station_metadata()
            station_group.write_metadata()

            survey_group.update_survey_metadata()
            survey_group.write_metadata()

            m.channel_summary.summarize()
