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

from mtpy.processing.aurora.process_aurora import AuroraProcessing
from mt_metadata.common import MTime
from mth5.helpers import close_open_files
from mtpy import MT, MTData


warnings.filterwarnings("ignore")
# =============================================================================
# path to already created MTH5 files.  These are usually one station per MTH5
survey_dir = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\CM2025\mth5")

# path to store EDI files and make directory if not alread exists
edi_path = survey_dir.joinpath("EDI_Files_aurora")
edi_path.mkdir(exist_ok=True)

# band setup file. This describes which frequency bands to process at
# each decimation level.
band_file = r"c:\Users\jpeacock\OneDrive - DOI\MTData\bandset.cfg"
band_file_4096 = r"c:\Users\jpeacock\OneDrive - DOI\MTData\bandset_4096.cfg"

# remote reference high frequency data, sometimes its better to not
rr_4096 = False
rr_geomag = True

# geomagnetic H5 file
geomag_mth5 = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\CM2025\usgs_geomag_frn_xy.h5")
# station name for geomagnetic observatory
rr_geomag_station = "Fresno"

# list of stations to process.
station_list = [
    {"local": "cm217", "remote": "cm215"},
]

# How to combined transfer functions for the various sample rates.
merge_dict = {
    256: {"period_min": 1.0 / 7.9, "period_max": 100},
    1: {"period_min": 100, "period_max": 10000},
    4096: {"period_min": 1.0 / 2048, "period_max": 1.0 / 8},
}

sample_rates = [4096, 256, 1]
# sample_rates = [256]  # sample rates to process

# loop over stations in the station list and process.
for station_dict in station_list:

    st = MTime().now()

    processing_dict = dict([(sr, {"config": None, "kernel_dataset": None}) for sr in sample_rates])

    # setup AuroraProcessing object
    ap = AuroraProcessing(merge_dictionary=merge_dict)
    ap.local_station_id = station_dict["local"]
    ap.local_mth5_path = survey_dir.joinpath(f"{ap.local_station_id}.h5")

    

    ## this will run defaults and remote reference each sample rate to
    ## the specified remote reference.
    # tf_processed = ap.process([4096, 256, 1])


    # if you want more control the you need to create a kernel dataset
    # and a configuration for each sample rate.

    for sample_rate in sample_rates:
        close_open_files()
        ap.df = None  # reset the dataframe
        if station_dict["remote"] is None:
            ap.remote_station_id = None
        elif sample_rate == 4096 and not rr_4096:
            ap.remote_station_id = None
        elif sample_rate == 1 and rr_geomag:
            ap.remote_station_id = rr_geomag_station
            ap.remote_mth5_path = geomag_mth5
        else:
            ap.remote_station_id = station_dict["remote"]
            ap.remote_mth5_path = survey_dir.joinpath(f"{ap.remote_station_id}.h5")


        # create run summary
        run_summary = ap.get_run_summary()
        run_summary.set_sample_rate(sample_rate, inplace=True)

        # create kernel dataset
        kernel_dataset = ap.create_kernel_dataset(
            run_summary=run_summary,
            local_station_id=ap.local_station_id,
            remote_station_id=ap.remote_station_id,
        )

        # drop runs that are too short
        if sample_rate == 4096:
            mimimum_run_duration = 100  # seconds
            band_setup_file = band_file_4096
        elif sample_rate == 256:
            mimimum_run_duration = 1000  # seconds
            band_setup_file = band_file
        elif sample_rate == 1:
            mimimum_run_duration = 3600 * 5  # seconds
            band_setup_file = band_file

        kernel_dataset.drop_runs_shorter_than(mimimum_run_duration)

        # create configuration object
        config = ap.create_config(
            kernel_dataset=kernel_dataset,
            add_coherence_weights=True,
            **{"emtf_band_file": band_setup_file,
               "input_channels": kernel_dataset.input_channels,
               "output_channels": kernel_dataset.output_channels,
               },
        )

        # add to processing dictionary
        processing_dict[sample_rate]["config"] = config
        processing_dict[sample_rate]["kernel_dataset"] = kernel_dataset

    ### process
    processed_dict = ap.process(
        processing_dict=processing_dict,
    )

    # plot each TF for each sample rate
    md = MTData()
    for sample_rate, processed in processed_dict.items():
        if "tf" not in processed:
            logger.warning(f"No transfer function for {sample_rate} Hz")
            continue
        md.add_station(processed["tf"], survey=f"sr_{sample_rate}")

    md.plot_mt_response(list(md.keys()), plot_style="compare", fig_num=2)

    # plot with MTpy
    try:
        combined = processed_dict["combined"]["tf"]
    except KeyError:
        raise ValueError("Processing did not complete successfully. Check logs.")
    
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
    logger.warning(f"Processing took: {str(diff).split('days')[-1].strip()} minutes")
    print("\a")