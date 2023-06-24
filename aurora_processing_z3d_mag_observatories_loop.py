#!/usr/bin/env python
# coding: utf-8

# =============================================================================
# Imports
# =============================================================================
from pathlib import Path
import warnings

from matplotlib import pyplot as plt

from mth5 import read_file
from mth5.io.zen import Z3DCollection
from mth5.mth5 import MTH5

from mtpy import MT

from aurora.config.config_creator import ConfigCreator
from aurora.pipelines.process_mth5 import process_mth5
from aurora.pipelines.run_summary import RunSummary
from aurora.transfer_function.kernel_dataset import KernelDataset

warnings.filterwarnings("ignore")

# =============================================================================


class ProcessMTH5ObsRR:
    """
    Process Zen data using magnetic observatory data as a remote reference.

    Observatory data is sample at 1 second, therefore the zen data is down
    sampled to 1 second using scipy.signal.resample_poly and then combined.
    The time gaps between schedule actions is set to be the mean values of the
    gap bookend values.

    The coils responses end around 1000 seconds so need to either extend those
    values or take caution in using those values.

    This assumes a separate MTH5 containing observatory data has been created.

    Steps:

        1. gather information about z3d files in given directory of
         survey_dir/station and build MTH5 with a 1s combined run
        2. create input objects for Aurora
        3. run aurora
        4. save edi file and combine with original edi


    """

    def __init__(
        self,
        station,
        survey_dir,
        rr_station="Fresno",
        rr_mth5_basename="usgs_geomag_frn_xy.h5",
        **kwargs,
    ):
        self.station = station
        self.survey_dir = Path(survey_dir)

        self.rr_station = rr_station
        self.rr_mth5_basename = rr_mth5_basename
        self.rr_mth5_path = self.survey_dir.joinpath(self.rr_mth5_basename)
        self._edi_folder = "EDI_files_birrp"
        self.sample_rate = 1
        self.combine = True
        self._mth5_basename = "_with_1s_run.h5"

        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def station(self):
        return self._station

    @station.setter
    def station(self, value):
        self._station = value

    @property
    def save_path(self):
        return self.survey_dir.joinpath(self.station)

    @property
    def mth5_path(self):
        return self.save_path.joinpath(f"{self.station}{self._mth5_basename}")

    @property
    def edi_path(self):
        return self.survey_dir.joinpath(self._edi_folder)

    @property
    def survey_dir(self):
        return self._survey_dir

    @survey_dir.setter
    def survey_dir(self, value):
        self._survey_dir = Path(value)

        if not self._survey_dir.exists():
            raise IOError(f"{value} is not an existing directory. Check Path.")

    @property
    def survey(self):
        if self._survey_dir:
            return self._survey_dir.name
        return None

    def make_mth5(self):
        ## get z3d files
        zc = Z3DCollection(self.save_path)
        runs = zc.get_runs(sample_rates=[4096, 1024, 256])
        zen_station = list(runs.keys())[0]

        # make MTH5 if not already build
        if not self.mth5_path.exists():

            with MTH5() as m:
                m.open_mth5(self.mth5_path)

                survey_group = m.add_survey(self.survey)
                for station_id in runs.keys():
                    station_group = survey_group.stations_group.add_station(
                        station_id
                    )
                    station_group.metadata.update(
                        zc.station_metadata_dict[station_id]
                    )
                    station_group.write_metadata()
                    if self.combine:
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
                    if self.combine:
                        run_list.append(run_group.to_runts())
                        if self.combine:
                            # Combine runs and down sample to 1 second.
                            combined_run = run_list[0].merge(
                                run_list[1:], new_sample_rate=1
                            )
                            combined_run.run_metadata.id = "sr1_0001"
                            combined_run_group = station_group.add_run(
                                "sr1_0001"
                            )
                            combined_run_group.from_runts(combined_run)
                            combined_run_group.update_run_metadata()

                    station_group.update_station_metadata()
                survey_group.update_survey_metadata()

            if self.combine:
                p = combined_run.plot()
                p.savefig(
                    self.save_path.parent.joinpath(
                        f"{self.station}_1s_ts.png"
                    ),
                    dpi=300,
                )
                plt.close("all")

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

    def _get_original_edi(self):
        return self.edi_path.joinpath(f"{self.station}.edi")

    def _has_original_edi(self):

        if not self._get_original_edi().exists():
            return False
        return True

    def merge_with_original(self, new_tf):
        if self._has_original_edi():

            original = MT()
            original.read(self._get_original_edi())

            # new = MT()
            # new.read(new_edi_fn)

            combine = original.merge(
                {"tf": new_tf, "period_min": 9, "period_max": None},
                period_max=8.5,
            )
            combine.write(
                fn=self.edi_path.joinpath(
                    f"{self.station}_rr_frn_combined_01.edi"
                )
            )

            combine.tf_id = f"{self.station}_rr_frn_combined"
            combine.survey_metadata.id = new_tf.survey_metadata.id

            self._add_tf_to_mth5(combine)

            p1 = combine.plot_mt_response(fig_num=5, plot_num=2)
            p1.save_plot(
                self.edi_path.joinpath(f"{self.station}_rr_frn_combined.png"),
                fig_dpi=300,
                close_plot=True,
            )

    def _add_tf_to_mth5(self, tf):
        """
        Add transfer function to MTH5

        :param tf: DESCRIPTION
        :type tf: TYPE
        :return: DESCRIPTION
        :rtype: TYPE

        """

        with MTH5() as m:
            m.open_mth5(self.mth5_path)
            m.add_transfer_function(tf)

    def process(self):

        zen_station = self.make_mth5()
        run_summary = self.make_run_summary()
        kernel_dataset = self.make_kernel_dataset(run_summary, zen_station)
        config = self.make_config(kernel_dataset)

        tf_cls = process_mth5(
            config,
            kernel_dataset,
            units="MT",
            show_plot=False,
            z_file_path=None,
        )

        tf_cls.tf_id = f"{self.station}_1s_rr_frn"
        tf_cls.survey_metadata.id = self.survey

        self._add_tf_to_mth5(tf_cls)

        edi = tf_cls.write(
            self.mth5_path.parent.joinpath(
                f"{self.station}_{self.sample_rate}_rr_frn.edi"
            )
        )

        self.merge_with_original(tf_cls)


# =============================================================================
# run
# =============================================================================

# p = ProcessMTH5ObsRR(
#     "gz316", Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\GZ2023")
# )
# p.process()

survey_dir = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\GZ2022")

for station_path in survey_dir.iterdir():
    station = station_path.name
    if "gz" in station and station_path.is_dir():
        try:
            p_obj = ProcessMTH5ObsRR(station, survey_dir)
            p_obj.process()

        except Exception as error:
            print("XXX==================================XXX")
            print(f"XXX Station {station} FAILED XXX")
            print(error)
            print("XXX==================================XXX")
