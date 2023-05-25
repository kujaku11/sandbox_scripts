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


class ProcessMTH5ObsRR:
    def __init__(self, station, survey_dir, rr_station="Fresno", **kwargs):
        self.survey_dir = survey_dir

        self.rr_station = rr_station
        self.rr_mth5_basename = "usgs_geomag_frn_xy.h5"
        self.rr_mth5_path = self.survey_dir.joinpath(self.rr_mth5_basename)
        self.edi_path = None
        self.sample_rate = 1
        self.combine = True
        self.mth5_path = None

        self.station = station

        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def station(self):
        return self._station

    @station.setter
    def station(self, value):
        self._station = value
        if self.survey_dir is not None:
            self.save_path = self.survey_dir.joinpath(value)
            self.mth5_path = self.save_path.joinpath(f"{value}_with_1s_run.h5")
            self.edi_path = self.survey_dir.joinpath("EDI_files_birrp")

    def make_mth5(self, survey="GZ2023"):
        ## get z3d files
        zc = Z3DCollection(self.save_path)
        runs = zc.get_runs(sample_rates=[4096, 1024, 256])
        zen_station = list(runs.keys())[0]

        # make MTH5 if not already build
        if not self.mth5_path.exists():

            m = MTH5()
            m.open_mth5(self.mth5_path)

            survey_group = m.add_survey(survey)
            for station_id in runs.keys():
                station_group = survey_group.stations_group.add_station(
                    station_id
                )
                station_group.metadata.update(
                    zc.station_metadata_dict[station_id]
                )
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
                if self.combine:
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

            if self.combine:
                print(combined_run.__str__())
                p = combined_run.plot()
                p.savefig(
                    save_path.parent.joinpath(f"station_ts.png"), dpi=300
                )

            return zen_station

    def make_run_summary(self):
        # create run summary
        mth5_run_summary = RunSummary()
        mth5_run_summary.from_mth5s([self.mth5_path, self.rr_mth5_path])
        run_summary = mth5_run_summary.clone()
        run_summary.add_duration()
        run_summary.df = run_summary.df[
            run_summary.df.sample_rate == self.sample_rate
        ].iloc[:]

        return run_summary

    def make_kernel_dataset(self, run_summary, zen_station):
        # create kernel dataset
        kernel_dataset = KernelDataset()
        kernel_dataset.from_run_summary(
            run_summary, zen_station, self.rr_station
        )
        kernel_dataset.drop_runs_shorter_than(100)

        return kernel_dataset

    def make_config(
        self,
        kernel_dataset,
        band_file=r"c:\Users\jpeacock\OneDrive - DOI\Documents\GitHub\aurora\aurora\config\emtf_band_setup\bs_six_level.cfg",
    ):
        # create configuration
        cc = ConfigCreator()
        config = cc.create_from_kernel_dataset(
            kernel_dataset,
            emtf_band_file=band_file,
        )

        ## set parameters in decimation levels
        for decimation in config.decimations:
            decimation.estimator.engine = "RME_RR"
            decimation.window.type = "dpss"
            decimation.window.additional_args = {"alpha": 2.5}
            decimation.output_channels = ["ex", "ey"]
            decimation.window.overlap = 64
            decimation.window.num_samples = 128

        return config

    def merge_with_original(self, new_edi_fn):
        original = MT()
        original.read(self.edi_path.joinpath(f"{self.station}.edi"))

        new = MT()
        new.read(new_edi_fn)

        combine = original.merge(
            {"tf": new, "period_min": 9, "period_max": None}, period_max=8.5
        )
        combine.write(
            fn=self.edi_path.joinpath(f"{self.station}_rr_mo_combined.edi")
        )

        p1 = combine.plot_mt_response(fig_num=5, plot_num=2)
        p1.save_plot(
            self.save_path.joinpath(f"{self.station}_mag_obs_combined.png"),
            fig_dpi=300,
            close_plot=True,
        )

    def process(self, survey="GZ2023"):

        zen_station = self.make_mth5(survey)
        run_summary = self.make_run_summary()
        kernel_dataset = self.make_kernel_dataset(run_summary, zen_station)

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

        self.merge_with_original(edi.fn)


# =============================================================================
# run
# =============================================================================

# survey_dir = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\GZ2023")

# for station_path in survey.iterdir():
#     if "gz" in station_path.name:
#         p_obj = ProcessMTH5ObsRR(station_path.stem, survey_dir)
