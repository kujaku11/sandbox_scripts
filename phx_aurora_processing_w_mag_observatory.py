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
        station_mth5_path,
        rr_station,
        rr_mth5_path,
        survey,
        **kwargs,
    ):
        self.station = station
        self.station_mth5_path = Path(station_mth5_path)

        self.rr_station = rr_station
        self.rr_mth5_path = Path(rr_mth5_path)
        self.sample_rate = 1
        self.survey = survey
        self.has_hz = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    def make_run_summary(self):
        # create run summary
        mth5_run_summary = RunSummary()
        mth5_run_summary.from_mth5s(
            [self.station_mth5_path, self.rr_mth5_path]
        )
        run_summary = mth5_run_summary.clone()
        run_summary.add_duration()
        run_summary.df = run_summary.df[
            run_summary.df.sample_rate == self.sample_rate
        ].iloc[:]

        return run_summary

    def make_kernel_dataset(self, run_summary):
        # create kernel dataset
        kernel_dataset = KernelDataset()
        kernel_dataset.from_run_summary(
            run_summary, self.station, self.rr_station
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

        config.channel_nomenclature.ex = "e1"
        config.channel_nomenclature.ey = "e2"
        config.channel_nomenclature.hx = "h1"
        config.channel_nomenclature.hy = "h2"
        config.channel_nomenclature.hz = "h3"

        ## set parameters in decimation levels
        for decimation in config.decimations:
            decimation.estimator.engine = "RME_RR"
            decimation.window.type = "dpss"
            decimation.window.additional_args = {"alpha": 2.5}
            if self.has_hz:
                decimation.output_channels = ["e1", "e2", "h3"]
            else:
                decimation.output_channels = ["e1", "e2"]

            decimation.input_channels = ["h1", "h2"]
            decimation.reference_channels = ["hx", "hy"]
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
                    f"{self.station}_rr_{self.rr_station}_combined_01.edi"
                )
            )

            combine.tf_id = f"{self.station}_rr_{self.rr_station}_combined"
            combine.survey_metadata.id = new_tf.survey_metadata.id

            self._add_tf_to_mth5(combine)

            p1 = combine.plot_mt_response(fig_num=5, plot_num=2)
            p1.save_plot(
                self.edi_path.joinpath(
                    f"{self.station}_rr_{self.rr_station}_combined.png"
                ),
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
            m.open_mth5(self.station_mth5_path)
            m.add_transfer_function(tf)

    def process(self):

        # zen_station = self.make_mth5()
        run_summary = self.make_run_summary()
        kernel_dataset = self.make_kernel_dataset(run_summary)
        config = self.make_config(kernel_dataset)

        tf_cls = process_mth5(
            config,
            kernel_dataset,
            units="MT",
            show_plot=False,
            z_file_path=None,
        )

        tf_cls.tf_id = f"{self.station}_1s_rr_{self.rr_station}"
        tf_cls.survey_metadata.id = self.survey

        self._add_tf_to_mth5(tf_cls)

        edi = tf_cls.write(
            self.station_mth5_path.parent.joinpath(
                f"{self.station}_{self.sample_rate}_rr_{self.rr_station}.edi"
            )
        )

        mt_obj = MT()
        mt_obj.read(edi.fn)
        p1 = mt_obj.plot_mt_response(fig_num=5, plot_num=2)
        p1.save_plot(
            self.station_mth5_path.parent.joinpath(
                f"{self.station}_rr_{self.rr_station}_combined.png"
            ),
            fig_dpi=300,
            close_plot=True,
        )

        # self.merge_with_original(tf_cls)
        return edi


# =============================================================================
# run
# =============================================================================

p_obj = ProcessMTH5ObsRR(
    "321",
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\Kilauea2023\phx\321_Phx\kl321_mth5_from_phoenix.h5",
    "Honolulu",
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\Kilauea2023\usgs_geomag_frn_hon_xy.h5",
    "KLA",
)
edi_obj = p_obj.process()
