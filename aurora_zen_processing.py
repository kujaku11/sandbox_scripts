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

from aurora.config.config_creator import ConfigCreator
from aurora.pipelines.process_mth5 import process_mth5
from mth5.processing.run_summary import RunSummary
from mth5.processing.kernel_dataset import KernelDataset

from mth5.helpers import close_open_files
from mth5.mth5 import MTH5

from mt_metadata.utils.mttime import MTime

from mtpy import MT

warnings.filterwarnings("ignore")
# =============================================================================
survey_dir = Path(
    r"d:\WD SmartWare.swstor\IGSWMBWGLTGG032\Volume.b5634234.da89.11e2.aa2b.806e6f6e6963\MT\SAGE2025"
)
edi_path = survey_dir.joinpath("EDI_Files_aurora")
# band_file = r"d:\SAGE2023\bandset.cfg"
band_file = r"c:\\Users\\jpeacock\\OneDrive - DOI\\MTData\bandset.cfg"
rr_4096 = False
rr_geomag = True
geomag_mth5 = survey_dir.joinpath("usgs_geomag_bou_xy.h5")
rr_geomag_station = "Boulder"

edi_path.mkdir(exist_ok=True)

station_list = [
    {"local": "sg2504", "remote": "sg2503"},
    # {"local": "sg2501", "remote": "sg2508"},
    # {"local": "sg2502", "remote": "sg2505"},
    # {"local": "sg2504", "remote": "sg2503"},
    # {"local": "sg2505", "remote": "sg2502"},
    # {"local": "sg2508", "remote": "sg2501"},
    # {"local": "sg2509", "remote": "sg2510"},
    # {"local": "sg2510", "remote": "sg2509"},
]

for station_dict in station_list:
    local_station = station_dict["local"]
    rr_station = station_dict["remote"]

    st = MTime().now()

    local_zen_station = local_station
    local_mth5 = survey_dir.joinpath("mth5", f"{local_station}.h5")

    if rr_station is not None:
        rr_zen_station = rr_station
        remote_mth5 = survey_dir.joinpath("mth5", f"{rr_station}.h5")
    else:
        remote_mth5 = None
    sample_rates = [4096, 256, 1]
    # sample_rates = [1]

    tf_list = []
    sr_processed = {4096: False, 256: False, 1: False}
    for sample_rate in sample_rates:
        close_open_files()
        mth5_run_summary = RunSummary()
        if rr_station is None or sample_rate == 4096:
            mth5_run_summary.from_mth5s([local_mth5])
        elif sample_rate == 1 and rr_geomag:
            mth5_run_summary.from_mth5s([local_mth5, geomag_mth5])

        else:
            mth5_run_summary.from_mth5s([local_mth5, remote_mth5])
        run_summary = mth5_run_summary.clone()
        run_summary.df = run_summary.df[
            run_summary.df.sample_rate == sample_rate
        ]
        # run_summary.add_duration()

        if sample_rate != 1:
            run_summary.df = run_summary.df[
                run_summary.df.end < "2025-06-24T18:00:00"
            ]
        else:
            run_summary.df.end[:] = "2025-06-24T18:00:00"

        kernel_dataset = KernelDataset()
        if rr_station is None or sample_rate == 4096:
            # run_summary.df = run_summary.df.iloc[0:1]
            kernel_dataset.from_run_summary(run_summary, local_zen_station)
        elif sample_rate == 1 and rr_geomag:
            kernel_dataset.from_run_summary(
                run_summary, local_zen_station, rr_geomag_station
            )
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
            emtf_band_file=band_file,
        )
        for decimation in config.decimations:
            if sample_rate == 4096:
                if rr_4096:
                    decimation.estimator.engine = "RME_RR"
                else:
                    decimation.estimator.engine = "RME"
                decimation.window.overlap = 128
                decimation.window.num_samples = 1024

            else:
                decimation.estimator.engine = "RME_RR"
                decimation.window.overlap = 64
                decimation.window.num_samples = 128
            decimation.window.type = "dpss"
            decimation.window.additional_args = {"alpha": 2.5}
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
                {
                    "tf": tf_list[1],
                    "period_min": 1.0 / 25,
                    "period_max": 10000,
                },
            ],
            period_max=1.0 / 26,
        )
    elif sr_processed[4096] == True and sr_processed[1] == True:
        combined = tf_list[0].merge(
            [
                {
                    "tf": tf_list[1],
                    "period_min": 1.0 / 8,
                    "period_max": 10000,
                },
            ],
            period_max=5,
        )
    else:
        combined = tf_list[0]
    combined.station = f"{local_station}"
    combined.tf_id = f"{local_station}_combined"

    edi = combined.write(edi_path.joinpath(f"{local_station}_combined.edi"))
    with MTH5() as m:
        m.open_mth5(local_mth5)
        m.add_transfer_function(combined)

    # plot with MTpy
    mt_obj = MT()
    mt_obj.survey_metadata = combined.survey_metadata
    mt_obj._transfer_function = combined._transfer_function
    p1 = mt_obj.plot_mt_response(fig_num=6, plot_num=2)
    p1.save_plot(
        edi_path.joinpath(f"{mt_obj.station}.png"),
        fig_dpi=300,
        close_plot=False,
    )

    et = MTime().now()

    diff = pd.Timedelta(et - st, unit="s")
    logger.warning(
        f"Processing took: {str(diff).split('days')[-1].strip()} minutes"
    )
    print("\a")
