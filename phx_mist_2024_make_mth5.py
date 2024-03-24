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
from mth5.io.phoenix.readers.calibrations import PhoenixCalibration

# =============================================================================

survey_dir = Path(r"c:\MT\ST2024\phx")

instrument_cals = {
    "10643": Path(r"c:\MT\ST2024\phx\1014\10643_65F9D6E8.rxcal.json"),
    "10521": Path(r"c:\MT\ST2024\phx\1014\10643_65F9D6E8.rxcal.json"),
    "10520": Path(r"c:\MT\ST2024\phx\1014\10643_65F9D6E8.rxcal.json"),
}

coil_cals = {
    "57514": PhoenixCalibration(
        cal_fn=Path(r"c:\MT\ST2024\phx\1014\57514_65F9CE33.scal.json")
    ),
    "57458": PhoenixCalibration(
        cal_fn=Path(r"c:\MT\ST2024\phx\1014\57458_65F9CE33.scal.json")
    ),
    "53408": PhoenixCalibration(
        cal_fn=Path(r"c:\MT\ST2024\phx\1014\53408_65F9CE33.scal.json")
    ),
    "57547": PhoenixCalibration(
        cal_fn=Path(r"c:\MT\ST2024\phx\1014\57514_65F9CE33.scal.json")
    ),
    "57509": PhoenixCalibration(
        cal_fn=Path(r"c:\MT\ST2024\phx\1014\57458_65F9CE33.scal.json")
    ),
    "53402": PhoenixCalibration(
        cal_fn=Path(r"c:\MT\ST2024\phx\1014\53408_65F9CE33.scal.json")
    ),
    "57511": PhoenixCalibration(
        cal_fn=Path(r"c:\MT\ST2024\phx\1014\57514_65F9CE33.scal.json")
    ),
    "57454": PhoenixCalibration(
        cal_fn=Path(r"c:\MT\ST2024\phx\1014\57458_65F9CE33.scal.json")
    ),
    "53421": PhoenixCalibration(
        cal_fn=Path(r"c:\MT\ST2024\phx\1014\53408_65F9CE33.scal.json")
    ),
}


# =============================================================================
#
# =============================================================================
station_list = [
    Path("c:/MT/ST2024/phx/1008"),
    Path("c:/MT/ST2024/phx/1033"),
    Path("c:/MT/ST2024/phx/1034"),
    Path("c:/MT/ST2024/phx/9006"),
]

for station_dir in station_list:
    if station_dir.is_dir():
        station = station_dir.name[0:]
        phx_collection = PhoenixCollection(file_path=station_dir)
        run_dict = phx_collection.get_runs(sample_rates=[150, 24000])

        with MTH5() as m:
            collection_metadata = phx_collection.metadata_dict[station]
            m.open_mth5(
                station_dir.joinpath(f"mist_{station}_mth5_from_phoenix.h5"),
                "w",
            )
            survey_metadata = collection_metadata.survey_metadata
            survey_group = m.add_survey(survey_metadata.id)
            for station_id, station_dict in run_dict.items():
                station_metadata = phx_collection.metadata_dict[
                    station
                ].station_metadata
                station_group = survey_group.stations_group.add_station(
                    station_metadata.id, station_metadata=station_metadata
                )
                for run_id, run_df in station_dict.items():
                    run_metadata = collection_metadata.run_metadata
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
                                    "channel_map": collection_metadata.channel_map,
                                    "rxcal_fn": instrument_cals[
                                        collection_metadata.instrument_id
                                    ],
                                },
                            )

                        except OSError:
                            print(
                                f"OSError: skipping {row.fn.name} likely too small"
                            )

                        if ch_ts.component in ["h1", "h2", "h3"]:

                            # for phx coils from generic response curves
                            if (
                                ch_ts.channel_metadata.sensor.id
                                in coil_cals.keys()
                            ):
                                pc = coil_cals[
                                    ch_ts.channel_metadata.sensor.id
                                ]
                                for key in pc.__dict__.keys():
                                    if key.startswith("h"):
                                        break
                                coil_fap = getattr(pc, key)

                            # add filter
                            ch_ts.channel_metadata.filter.name.append(
                                coil_fap.name
                            )
                            ch_ts.channel_metadata.filter.applied.append(True)
                            ch_ts.channel_response.filters_list.append(
                                coil_fap
                            )

                        # add channel to the run group
                        ch_dataset = run_group.from_channel_ts(ch_ts)

                    run_group.update_metadata()
            station_group.update_metadata()
            survey_group.update_metadata()

            m.channel_summary.summarize()
