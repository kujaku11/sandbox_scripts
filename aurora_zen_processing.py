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

from aurora.config.config_creator import ConfigCreator
from aurora.pipelines.process_mth5 import process_mth5
from aurora.pipelines.run_summary import RunSummary
from aurora.transfer_function.kernel_dataset import KernelDataset

from mth5.helpers import close_open_files
from mth5.mth5 import MTH5

from mt_metadata.utils.mttime import MTime

from mtpy import MT

warnings.filterwarnings("ignore")
# =============================================================================
survey_dir = Path(r"c:\MT\BV2023")
edi_path = survey_dir.joinpath("EDI_Files_aurora")

for local_station, rr_station in zip(
    ["bv77", "bv96", "bv97", "bv55", "bv62"],
    ["bv55", "bv77", "bv77", "bv77", "bv77"],
):

    st = MTime().now()
    local_zen_station = local_station[2:]
    local_mth5 = survey_dir.joinpath("mth5", f"{local_station}_with_1s_run.h5")

    rr_zen_station = rr_station[2:]
    remote_mth5 = survey_dir.joinpath("mth5", f"{rr_station}_with_1s_run.h5")

    sample_rates = [4096, 256, 1]
    # sample_rates = [1]

    tf_list = []
    sr_processed = {}
    for sample_rate in sample_rates:
        close_open_files()
        mth5_run_summary = RunSummary()
        if sample_rate == 4096:
            mth5_run_summary.from_mth5s([local_mth5])
        else:
            mth5_run_summary.from_mth5s([local_mth5, remote_mth5])
        run_summary = mth5_run_summary.clone()
        run_summary.add_duration()
        run_summary.df = run_summary.df[run_summary.df.sample_rate == sample_rate]

        kernel_dataset = KernelDataset()
        if sample_rate == 4096:
            kernel_dataset.from_run_summary(run_summary, local_zen_station)
        else:
            kernel_dataset.from_run_summary(
                run_summary, local_zen_station, rr_zen_station
            )
        if sample_rate == 4096:
            mimimum_run_duration = 100  # seconds
        elif sample_rate == 256:
            mimimum_run_duration = 1000  # seconds
        elif sample_rate == 1:
            mimimum_run_duration = 3600 * 5  # seconds
        kernel_dataset.drop_runs_shorter_than(mimimum_run_duration)

        cc = ConfigCreator()
        config = cc.create_from_kernel_dataset(
            kernel_dataset,
            emtf_band_file=r"c:\Users\peaco\Documents\GitHub\aurora\aurora\config\emtf_band_setup\bs_six_level.cfg",
        )
        for decimation in config.decimations:
            if sample_rate == 4096:
                decimation.estimator.engine = "RME"
            else:
                decimation.estimator.engine = "RME_RR"
            decimation.window.type = "dpss"
            decimation.window.additional_args = {"alpha": 2.5}
            decimation.window.overlap = 64
            decimation.window.num_samples = 128
            decimation.output_channels = ["ex", "ey", "hz"]
        # process
        try:
            tf_obj = process_mth5(
                config,
                kernel_dataset,
                units="MT",
                show_plot=False,
                z_file_path=None,
            )
            tf_obj.tf_id = f"{local_station}_{sample_rate}"

            tf_list.append(tf_obj)
            sr_processed[sample_rate] = True

            with MTH5() as m:
                m.open_mth5(local_mth5)
                m.add_transfer_function(tf_obj)
        except Exception as error:
            close_open_files()
            logger.exception(error)
            logger.error(f"skipping {sample_rate}")
            sr_processed[sample_rate] = False
    if (
        sr_processed[4096] == True
        and sr_processed[256] == True
        and sr_processed[1] == True
    ):
        combined = tf_list[0].merge(
            [
                {"tf": tf_list[1], "period_min": 1.0 / 25, "period_max": 100},
                {"tf": tf_list[2], "period_min": 100, "period_max": 10000},
            ],
            period_max=1.0 / 26,
        )
    elif sr_processed[256] == True and sr_processed[1] == True:
        combined = tf_list[0].merge(
            [
                {"tf": tf_list[1], "period_min": 100, "period_max": 10000},
            ],
            period_max=100,
        )
    elif sr_processed[4096] == True and sr_processed[256] == True:
        combined = tf_list[0].merge(
            [
                {"tf": tf_list[1], "period_min": 1.0 / 25, "period_max": 10000},
            ],
            period_max=1.0 / 26,
        )
    else:
        print("Something went wrong, check logs.")
    combined.station = f"bv{combined.station}"
    combined.tf_id = f"bv{combined.station}_combined"

    edi = combined.write(edi_path.joinpath(f"{combined.station}_combined.edi"))

    # plot with MTpy
    mt_obj = MT()
    mt_obj.station_metadata = combined.station_metadata
    mt_obj.survey_metadata = combined.survey_metadata
    mt_obj._transfer_function = combined._transfer_function
    p1 = mt_obj.plot_mt_response(fig_num=6, plot_num=2)
    p1.save_plot(
        edi_path.joinpath(f"{mt_obj.station}.png"), fig_dpi=300, close_plot=False
    )

    et = MTime().now()

    diff = et - st
    logger.warning(f"Processing took: {diff % 60:02.0f}:{diff // 60:02.0f} minutes")
    print("\a")
