#!/usr/bin/env python
# coding: utf-8

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path

from mth5 import read_file
from mth5.io.zen import Z3DCollection, zen_tools
from mth5.mth5 import MTH5
from mtpy import MT

# Required imports for the program.
import warnings
from pathlib import Path

from aurora.config.config_creator import ConfigCreator
from aurora.pipelines.process_mth5 import process_mth5
from aurora.pipelines.run_summary import RunSummary
from aurora.transfer_function.kernel_dataset import KernelDataset

from mth5.helpers import close_open_files

warnings.filterwarnings("ignore")

# =============================================================================
# ## Important Parameters.

station = "gz316"
survey_dir = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\GZ2023")
save_path = survey_dir.joinpath(station)
mth5_path = save_path.joinpath(f"{station}_with_1s_run.h5")
edi_path = survey_dir.joinpath("EDI_files_birrp")
combine = True
rr_station = "Fresno"
rr_zen_station = "Fresno"
remote_mth5_path = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\GZ2023\usgs_geomag_frn_xy.h5"
)
sample_rate = 1


## get z3d files
zc = Z3DCollection(save_path)
runs = zc.get_runs(sample_rates=[4096, 1024, 256])
zen_station = list(runs.keys())[0]

# make MTH5 if not already build
if not mth5_path.exists():
    m = MTH5()
    m.open_mth5(mth5_path)

    survey_group = m.add_survey("GZ2023")
    for station_id in runs.keys():
        station_group = survey_group.stations_group.add_station(station_id)
        station_group.metadata.update(zc.station_metadata_dict[station_id])
        station_group.write_metadata()
        if combine:
            run_list = []
        for run_id, run_df in runs[station_id].items():
            run_group = station_group.add_run(run_id)
            for row in run_df.itertuples():
                ch_ts = read_file(
                    row.fn,
                    calibration_fn=r"c:\\Users\\jpeacock\\OneDrive - DOI\\MTData\\antenna_20190411.cal",
                )
                run_group.from_channel_ts(ch_ts)
                run_group.update_run_metadata()
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
                combined_run_group.update_run_metadata()

        station_group.update_station_metadata()
    survey_group.update_survey_metadata()

    m.close_mth5()

    if combine:
        print(combined_run.__str__())
        p = combined_run.plot()
        p.savefig(save_path.parent.joinpath(f"station_ts.png"), dpi=300)

# create run summary
mth5_run_summary = RunSummary()
mth5_run_summary.from_mth5s([mth5_path, remote_mth5_path])
run_summary = mth5_run_summary.clone()
run_summary.add_duration()
run_summary.df = run_summary.df[
    run_summary.df.sample_rate == sample_rate
].iloc[:]

# create kernel dataset
kernel_dataset = KernelDataset()
kernel_dataset.from_run_summary(run_summary, zen_station, rr_zen_station)
kernel_dataset.drop_runs_shorter_than(100)

# create configuration
cc = ConfigCreator()
config = cc.create_from_kernel_dataset(
    kernel_dataset,
    emtf_band_file=r"c:\Users\jpeacock\OneDrive - DOI\Documents\GitHub\aurora\aurora\config\emtf_band_setup\bs_six_level.cfg",
)

## set parameters in decimation levels
for decimation in config.decimations:
    decimation.estimator.engine = "RME_RR"
    decimation.window.type = "dpss"
    decimation.window.additional_args = {"alpha": 2.5}
    decimation.output_channels = ["ex", "ey"]
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
    mth5_path.parent.joinpath(f"{station}_{sample_rate}_rr_mo.edi")
)

original = MT()
original.read(edi_path.joinpath(f"{station}.edi"))

new = MT()
new.read(edi.fn)

combine = original.merge(
    {"tf": new, "period_min": 9, "period_max": None}, period_max=8.5
)
combine.write(fn=edi_path.joinpath(f"{station}_rr_mo_combined.edi"))

p1 = combine.plot_mt_response(fig_num=5, plot_num=2)
p1.save_plot(
    save_path.joinpath(f"{station}_mag_obs_combined.png"),
    fig_dpi=300,
    close_plot=False,
)
