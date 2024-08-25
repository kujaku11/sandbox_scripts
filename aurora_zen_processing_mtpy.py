# -*- coding: utf-8 -*-
"""

Created on Sun Jul 23 14:26:50 2023

:author: Jared Peacock

:license: MIT

"""
# =============================================================================
#
# =============================================================================
import warnings
from pathlib import Path
from loguru import logger
import pandas as pd

# from aurora.config.config_creator import ConfigCreator
# from aurora.pipelines.process_mth5 import process_mth5
# from aurora.pipelines.run_summary import RunSummary
# from aurora.transfer_function.kernel_dataset import KernelDataset

from mtpy.processing import AuroraProcessing

# from mth5.helpers import close_open_files
# from mth5.mth5 import MTH5

from mt_metadata.utils.mttime import MTime


warnings.filterwarnings("ignore")
# =============================================================================
# survey_dir = Path(r"c:\MT\BV2023")
survey_dir = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\MB")
# survey_dir = Path(r"d:\SAGE2024")
edi_path = survey_dir.joinpath("EDI_Files_aurora")
# band_file = r"d:\SAGE2023\bandset.cfg"
band_file = r"c:\Users\jpeacock\OneDrive - DOI\MTData\bandset.cfg"
rr_4096 = False
rr_geomag = False
geomag_mth5 = (
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2024\usgs_geomag_bou_xy.h5"
)
rr_geomag_station = "Boulder"

edi_path.mkdir(exist_ok=True)

station_list = [
    {"local": "mb99", "remote": "mb86"},
]

merge_dict = {
    256: {"period_min": 1.0 / 25, "period_max": 100},
    1: {"period_min": 100, "period_max": 10000},
    4096: {"period_min": 1.0 / 2000, "period_max": 1.0 / 26},
}

for station_dict in station_list:

    st = MTime().now()

    ap = AuroraProcessing(merge_dictionary=merge_dict)
    ap.local_station_id = station_dict["local"]
    ap.remote_station_id = station_dict["remote"]

    local_zen_station = ap.local_station_id
    ap.local_mth5_path = survey_dir.joinpath(
        "mth5", f"{ap.local_station_id}_with_1s_run.h5"
    )

    if ap.remote_station_id is not None:
        rr_zen_station = ap.remote_station_id
        ap.remote_mth5_path = survey_dir.joinpath(
            "mth5", f"{ap.remote_station_id}_with_1s_run.h5"
        )
    else:
        remote_mth5 = None

    ap.run_summary = ap.get_run_summary()

    ## this will run defaults and remote reference each sample rate to
    ## the specified remote reference.
    tf_processed = ap.process([4096, 256, 1])

    ## if you want more control the you need to create a kernel dataset
    ## and a configuration for each sample rate.
    ## 4096
    # build kernel dataset
    # if rr_4096:
    #     kds_4096 = ap.create_kernel_dataset(sample_rate=4096)
    # else:
    #     kds_4096 = ap.create_kernel_dataset(
    #         remote_station_id=None, sample_rate=4096
    #     )

    # # build config
    # config = ap.create_config

    # processing_dict = {}

    # for sr in [4096, 256, 1]:

    # sample_rates =
    # # sample_rates = [1]

    # tf_list = []
    # sr_processed = {4096: False, 256: False, 1: False}
    # for sample_rate in sample_rates:
    #     close_open_files()
    #     mth5_run_summary = RunSummary()
    #     if rr_station is None or sample_rate == 4096:
    #         mth5_run_summary.from_mth5s([local_mth5])
    #     elif sample_rate == 1 and rr_geomag:
    #         mth5_run_summary.from_mth5s([local_mth5, geomag_mth5])

    #     else:
    #         mth5_run_summary.from_mth5s([local_mth5, remote_mth5])
    #     run_summary = mth5_run_summary.clone()
    #     run_summary.df = run_summary.df[
    #         run_summary.df.sample_rate == sample_rate
    #     ]
    #     run_summary.add_duration()

    #     kernel_dataset = KernelDataset()
    #     if rr_station is None or sample_rate == 4096:
    #         # run_summary.df = run_summary.df.iloc[0:1]
    #         kernel_dataset.from_run_summary(run_summary, local_zen_station)
    #     elif sample_rate == 1 and rr_geomag:
    #         kernel_dataset.from_run_summary(
    #             run_summary, local_zen_station, rr_geomag_station
    #         )
    #     else:
    #         kernel_dataset.from_run_summary(
    #             run_summary, local_zen_station, rr_zen_station
    #         )
    #     if sample_rate == 4096:
    #         mimimum_run_duration = 100  # seconds
    #     elif sample_rate == 256:
    #         mimimum_run_duration = 1000  # seconds
    #     elif sample_rate == 1:
    #         mimimum_run_duration = 3600 * 5  # seconds
    #     kernel_dataset.drop_runs_shorter_than(mimimum_run_duration)

    #     cc = ConfigCreator()
    #     config = cc.create_from_kernel_dataset(
    #         kernel_dataset,
    #         emtf_band_file=band_file,
    #     )
    #     for decimation in config.decimations:
    #         if sample_rate == 4096:
    #             if rr_4096:
    #                 decimation.estimator.engine = "RME_RR"
    #             else:
    #                 decimation.estimator.engine = "RME"
    #             decimation.window.overlap = 128
    #             decimation.window.num_samples = 1024

    #         else:
    #             decimation.estimator.engine = "RME_RR"
    #             decimation.window.overlap = 64
    #             decimation.window.num_samples = 128
    #         decimation.window.type = "dpss"
    #         decimation.window.additional_args = {"alpha": 2.5}
    #         decimation.output_channels = ["ex", "ey", "hz"]
    #     # process
    #     try:
    #         tf_obj = process_mth5(
    #             config,
    #             kernel_dataset,
    #             units="MT",
    #             show_plot=False,
    #             z_file_path=None,
    #         )
    #         tf_obj.tf_id = f"{local_station}_{sample_rate}"

    #         tf_list.append(tf_obj)
    #         sr_processed[sample_rate] = True

    #         with MTH5() as m:
    #             m.open_mth5(local_mth5)
    #             m.add_transfer_function(tf_obj)
    #     except Exception as error:
    #         close_open_files()
    #         logger.exception(error)
    #         logger.error(f"skipping {sample_rate}")
    #         sr_processed[sample_rate] = False
    # if (
    #     sr_processed[4096] == True
    #     and sr_processed[256] == True
    #     and sr_processed[1] == True
    # ):
    #     combined = tf_list[0].merge(
    #         [
    #             {"tf": tf_list[1], "period_min": 1.0 / 25, "period_max": 100},
    #             {"tf": tf_list[2], "period_min": 100, "period_max": 10000},
    #         ],
    #         period_max=1.0 / 26,
    #     )
    # elif sr_processed[256] == True and sr_processed[1] == True:
    #     combined = tf_list[0].merge(
    #         [
    #             {"tf": tf_list[1], "period_min": 100, "period_max": 10000},
    #         ],
    #         period_max=100,
    #     )
    # elif sr_processed[4096] == True and sr_processed[256] == True:
    #     combined = tf_list[0].merge(
    #         [
    #             {
    #                 "tf": tf_list[1],
    #                 "period_min": 1.0 / 25,
    #                 "period_max": 10000,
    #             },
    #         ],
    #         period_max=1.0 / 26,
    #     )
    # elif sr_processed[4096] == True and sr_processed[1] == True:
    #     combined = tf_list[0].merge(
    #         [
    #             {
    #                 "tf": tf_list[1],
    #                 "period_min": 1.0 / 8,
    #                 "period_max": 10000,
    #             },
    #         ],
    #         period_max=5,
    #     )
    # else:
    #     print("Something went wrong, check logs.")
    # combined.station = f"{combined.station}"
    # combined.tf_id = f"{combined.station}_combined"

    # edi = combined.write(edi_path.joinpath(f"{combined.station}_combined.edi"))
    # with MTH5() as m:
    #     m.open_mth5(local_mth5)
    #     m.add_transfer_function(combined)

    # # plot with MTpy
    # mt_obj = MT()
    # mt_obj.survey_metadata = combined.survey_metadata
    # mt_obj._transfer_function = combined._transfer_function
    # p1 = mt_obj.plot_mt_response(fig_num=6, plot_num=2)
    # p1.save_plot(
    #     edi_path.joinpath(f"{mt_obj.station}.png"),
    #     fig_dpi=300,
    #     close_plot=False,
    # )

    et = MTime().now()

    diff = pd.Timedelta(et - st, unit="s")
    logger.warning(
        f"Processing took: {str(diff).split('days')[-1].strip()} minutes"
    )
    print("\a")
