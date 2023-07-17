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

from aurora.config.config_creator import ConfigCreator
from aurora.pipelines.process_mth5 import process_mth5
from aurora.pipelines.run_summary import RunSummary
from aurora.transfer_function.kernel_dataset import KernelDataset

from mtpy import MT

warnings.filterwarnings("ignore")
# =============================================================================

local_station = "102"
local_mth5_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2023\102_060923\mth5_from_phoenix.h5"
)

remote_station = "Tucson"
remote_mth5_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\SAGE2023\usgs_geomag_bou_tuc_xy.h5"
)


sample_rate = 1

# =============================================================================
mth5_run_summary = RunSummary()
if remote_mth5_path is not None:
    mth5_run_summary.from_mth5s([local_mth5_path, remote_mth5_path])
else:
    mth5_run_summary.from_mth5s([local_mth5_path])
run_summary = mth5_run_summary.clone()
run_summary.add_duration()
run_summary.df = run_summary.df[run_summary.df.sample_rate == sample_rate].iloc[
    :
]
run_summary.mini_summary


kernel_dataset = KernelDataset()
if remote_station is not None:
    kernel_dataset.from_run_summary(
        RunSummary(df=run_summary.df), local_station, remote_station
    )
else:
    kernel_dataset.from_run_summary(
        RunSummary(df=run_summary.df), local_station
    )
mimimum_run_duration = 3600 * 5  # seconds
kernel_dataset.drop_runs_shorter_than(mimimum_run_duration)
kernel_dataset.mini_summary


cc = ConfigCreator()
config = cc.create_from_kernel_dataset(
    kernel_dataset,
    emtf_band_file=r"c:\Users\jpeacock\OneDrive - DOI\Documents\GitHub\aurora\aurora\config\emtf_band_setup\bs_six_level.cfg",
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
print("=== FINISHED ===")

edi = tf_cls.write(
    local_mth5_path.parent.joinpath(f"{local_station}_{sample_rate}.edi")
)

# plot with MTpy
mt_obj = MT()
mt_obj.read(edi.fn)
p1 = mt_obj.plot_mt_response(fig_num=1, plot_num=2)
p1.save_plot(
    local_mth5_path.parent.joinpath(f"{edi.fn.stem}.png"),
    fig_dpi=300,
    close_plot=False,
)
