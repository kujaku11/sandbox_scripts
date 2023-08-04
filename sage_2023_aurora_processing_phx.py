#!/usr/bin/env python
# coding: utf-8

# # Processing SAGE Phoenix data with Aurora
#
# This is an example of how to process data collected with a Phoenix MTU-5c data with Aurora.  For now this assumes that an MTH5 has already been created.

# ## Process With Aurora

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import warnings
from loguru import logger

from aurora.config.config_creator import ConfigCreator
from aurora.pipelines.process_mth5 import process_mth5
from aurora.pipelines.run_summary import RunSummary
from aurora.transfer_function.kernel_dataset import KernelDataset

from mt_metadata.utils.mttime import MTime

from mtpy import MT

warnings.filterwarnings("ignore")
# =============================================================================

local_station = "108"
local_mth5_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2023\108_061223\vc108_mth5_from_phoenix.h5"
)

remote_station = None
remote_mth5_path = None
# remote_station = "Boulder"
# remote_mth5_path = Path(
#     r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2023\usgs_geomag_bou_tuc_hx_hy.h5"
# )

start_time = MTime().now()


bursts = (
    list(range(5))
    + list(range(50, 60, 1))
    + list(range(100, 110, 1))
    #    + list(range(150, 155, 1))
    #    + list(range(100, 105, 1))
    # + list(range(200, 205, 1))
    # + list(range(250, 255, 1))
    # + list(range(300, 305, 1))
    # + list(range(350, 355, 1))
)

tf_list = []
for ii, sample_rate in enumerate([150, 24000], 1):
    st = MTime().now()

    mth5_run_summary = RunSummary()
    if remote_mth5_path is not None:
        mth5_run_summary.from_mth5s([local_mth5_path, remote_mth5_path])
    else:
        mth5_run_summary.from_mth5s([local_mth5_path])
    run_summary = mth5_run_summary.clone()
    run_summary.add_duration()
    if sample_rate == 150:
        run_summary.df = run_summary.df[
            run_summary.df.sample_rate == sample_rate
        ]
    elif sample_rate == 24000:
        run_summary.df = run_summary.df[
            run_summary.df.sample_rate == sample_rate
        ].iloc[bursts]

    # KERNEL DATASET
    kernel_dataset = KernelDataset()
    if remote_station is not None:
        kernel_dataset.from_run_summary(
            RunSummary(df=run_summary.df), local_station, remote_station
        )
    else:
        kernel_dataset.from_run_summary(
            RunSummary(df=run_summary.df), local_station
        )
    if sample_rate == 150:
        mimimum_run_duration = 3600  # seconds
    elif sample_rate == 24000:
        mimimum_run_duration = 1
    elif sample_rate == 1:
        minimum_run_duration = 3600 * 6
    kernel_dataset.drop_runs_shorter_than(mimimum_run_duration)

    cc = ConfigCreator()
    if sample_rate == 150:
        config = cc.create_from_kernel_dataset(
            kernel_dataset,
            emtf_band_file=r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2023\bandset.cfg",
        )
    elif sample_rate == 24000:
        config = cc.create_from_kernel_dataset(
            kernel_dataset,
            emtf_band_file=r"c:\Users\jpeacock\OneDrive - DOI\Documents\GitHub\aurora\aurora\config\emtf_band_setup\bs_four_level.cfg",
        )

    # need to update the channel nomenclature to what phoenix uses
    config.channel_nomenclature.ex = "e1"
    config.channel_nomenclature.ey = "e2"
    config.channel_nomenclature.hx = "h1"
    config.channel_nomenclature.hy = "h2"
    config.channel_nomenclature.hz = "h3"

    for decimation in config.decimations:
        if remote_station is not None:
            decimation.estimator.engine = "RME_RR"
        else:
            decimation.estimator.engine = "RME"
        decimation.window.type = "dpss"
        decimation.window.additional_args = {"alpha": 2.5}
        decimation.output_channels = ["e1", "e2", "h3"]
        decimation.input_channels = ["h1", "h2"]
        decimation.window.overlap = 64
        decimation.window.num_samples = 128

    tf_cls = process_mth5(
        config,
        kernel_dataset,
        units="MT",
        show_plot=False,
        z_file_path=None,
    )

    edi = tf_cls.write(
        local_mth5_path.parent.joinpath(f"{local_station}_{sample_rate}.edi")
    )

    # plot with MTpy
    mt_obj = MT()
    mt_obj.read(edi.fn)
    p1 = mt_obj.plot_mt_response(fig_num=ii, plot_num=2)
    p1.save_plot(
        local_mth5_path.parent.joinpath(f"{edi.fn.stem}.png"),
        fig_dpi=300,
        close_plot=False,
    )

    tf_list.append(tf_cls)

    et = MTime().now()
    dt = et - st

    logger.info(f"FINISHED: took {int((dt) // 60):02}:{(dt) % 60:02} minutes")

### merge
if len(tf_list) > 1:
    combined_tf = tf_list[1].merge(tf_list[0], period_max=0.03)

    edi = combined_tf.write(
        local_mth5_path.parent.joinpath(f"val{local_station}_combined.edi")
    )
    mt_obj = MT()
    mt_obj.read(edi.fn)
    p1 = mt_obj.plot_mt_response(fig_num=ii + 1, plot_num=2)
    p1.save_plot(
        local_mth5_path.parent.joinpath(f"{edi.fn.stem}.png"),
        fig_dpi=300,
        close_plot=False,
    )


end_time = MTime().now()
total_time = end_time - start_time

logger.info(
    f"FINISHED: took {int((total_time) // 60):02}:{(total_time) % 60:02} minutes"
)
