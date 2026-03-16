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
import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt

plt.ioff()

warnings.filterwarnings("ignore")

# =============================================================================
# Paths
# =============================================================================
# path to already created MTH5 files.  These are usually one station per MTH5
survey_dir = Path(r"c:\Users\jpeacock\OneDrive - DOI\MTData\CL2025\mth5")

# path to store EDI files and make directory if not already exists
edi_path = survey_dir.joinpath("EDI_Files_aurora_geomag_rr_boulder")
edi_path.mkdir(exist_ok=True)

# --- NEW: path to store logs ---
log_path = survey_dir.joinpath("logs")
log_path.mkdir(exist_ok=True)

# =============================================================================
# Config
# =============================================================================
# band setup file. This describes which frequency bands to process at
# each decimation level.
band_file = r"c:\Users\jpeacock\OneDrive - DOI\MTData\bandset.cfg"
band_file_4096 = r"c:\Users\jpeacock\OneDrive - DOI\MTData\bandset_4096.cfg"

# remote reference high frequency data, sometimes its better to not
rr_4096 = False
rr_geomag = True
use_coherence_weighting = True
# geomagnetic H5 file
geomag_mth5 = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MTData\CL2025\mth5\usgs_geomag_bou_xy.h5"
)
# station name for geomagnetic observatory
rr_geomag_station = "Boulder"

# list of stations to process.
station_list = [
    # {"local": "cl501", "remote": "cl507"},
    # {"local": "cl502", "remote": "cl507"},
    # {"local": "cl507", "remote": "cl502"},
    # {"local": "cl508", "remote": "cl530"},
    # {"local": "cl510", "remote": "cl526"},
    # {"local": "cl514", "remote": "cl526"},
    # {"local": "cl516", "remote": "cl526"},
    # {"local": "cl518", "remote": "cl532"},
    # {"local": "cl524", "remote": "cl530"},
    # {"local": "cl526", "remote": "cl510"},
    # {"local": "cl529", "remote": "cl530"},
    # {"local": "cl530", "remote": "cl524"},
    # {"local": "cl532", "remote": "cl518"},  # redo
    # {"local": "cl534", "remote": "cl551"},  # redo
    # {"local": "cl535", "remote": "cl590"},
    # {"local": "cl536", "remote": "cl518"},
    # {"local": "cl538", "remote": "cl547"},
    # {"local": "cl539", "remote": "cl518"},
    # {"local": "cl541", "remote": "cl534"},
    # {"local": "cl542", "remote": "cl535"},
    # {"local": "cl543", "remote": "cl535"},
    # {"local": "cl546", "remote": "cl547"},
    # {"local": "cl547", "remote": "cl546"},
    # {"local": "cl551", "remote": "cl534"},
    # {"local": "cl553", "remote": "cl507"},
    # {"local": "cl590", "remote": "cl535"},
]

# How to combined transfer functions for the various sample rates.
merge_dict = {
    256: {"period_min": 1.0 / 7.9, "period_max": 100},
    1: {"period_min": 100, "period_max": 10000},
    4096: {"period_min": 1.0 / 2048, "period_max": 1.0 / 8},
}

sample_rates = [4096, 256, 1]

# =============================================================================
# Logging Setup (Option B)
# =============================================================================

# Optional: add a master "batch" log to capture everything
master_log_file = log_path.joinpath("batch_run.log")
master_sink_id = logger.add(
    master_log_file,
    level="INFO",
    rotation="100 MB",
    retention="60 days",
    enqueue=True,
    backtrace=True,
    diagnose=False,  # set True if you want variable values in tracebacks
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
)

# Pre-register one sink per station using a filter that matches extra["station"]
station_sink_ids = {}
for sd in station_list:
    sid = sd["local"]
    station_log_file = log_path.joinpath(f"{sid}.log")
    station_sink_ids[sid] = logger.add(
        station_log_file,
        level="INFO",
        rotation="50 MB",  # or "daily"
        retention="30 days",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        # Only route records that carry extra['station'] == sid
        filter=lambda record, sid=sid: record["extra"].get("station") == sid,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | "
            "station={extra[station]} | {message}"
        ),
    )

# # Optional: keep a console sink (nice for real-time)
# console_sink_id = logger.add(
#     lambda msg: print(msg, end=""),
#     level="INFO",
#     format="{time:HH:mm:ss} | {level:<8} | {message}",
# )

# =============================================================================
# Processing Loop
# =============================================================================
for station_dict in station_list:
    station_id = station_dict["local"]

    # Contextualize all logs within this block with station=<station_id>
    with logger.contextualize(station=station_id):
        st = MTime().now()

        try:
            processing_dict = dict(
                [(sr, {"config": None, "kernel_dataset": None}) for sr in sample_rates]
            )

            # setup AuroraProcessing object
            ap = AuroraProcessing(merge_dictionary=merge_dict)
            ap.local_station_id = station_id
            ap.local_mth5_path = survey_dir.joinpath(f"{ap.local_station_id}.h5")

            logger.info("Starting processing for {}", station_id)

            ## this will run defaults and remote reference each sample rate to
            ## the specified remote reference.
            # tf_processed = ap.process([4096, 256, 1])

            # if you want more control the you need to create a kernel dataset
            # and a configuration for each sample rate.

            for sample_rate in sample_rates:
                close_open_files()
                ap.df = None  # reset the dataframe
                if station_dict["remote"] is None and not rr_geomag:
                    ap.remote_station_id = None
                elif sample_rate == 4096 and not rr_4096:
                    ap.remote_station_id = None
                elif sample_rate == 1 and rr_geomag:
                    ap.remote_station_id = rr_geomag_station
                    ap.remote_mth5_path = geomag_mth5
                else:
                    ap.remote_station_id = station_dict["remote"]
                    ap.remote_mth5_path = survey_dir.joinpath(
                        f"{ap.remote_station_id}.h5"
                    )

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
                    add_coherence_weights=use_coherence_weighting,
                    **{
                        "emtf_band_file": band_setup_file,
                        "input_channels": kernel_dataset.input_channels,
                        "output_channels": kernel_dataset.output_channels,
                        "save_fcs": False,
                        "save_fcs_type": "h5",
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
                    logger.warning("No transfer function for {} Hz", sample_rate)
                    continue
                md.add_station(processed["tf"], survey=f"sr_{sample_rate}")

            p2 = md.plot_mt_response(
                list(md.keys())[::-1], plot_style="compare", fig_num=2
            )
            p2.save_plot(
                edi_path.joinpath(f"{ap.local_station_id}_tfs.png"),
                fig_dpi=300,
                close_plot=True,
            )

            # plot with MTpy
            try:
                combined = processed_dict["combined"]["tf"]
            except KeyError:
                raise ValueError(
                    "Processing did not complete successfully. Check logs."
                )

            mt_obj = MT()
            mt_obj.survey_metadata = combined.survey_metadata
            mt_obj._transfer_function = combined._transfer_function
            mt_obj.write(edi_path.joinpath(f"{mt_obj.station}.edi"), file_type="edi")
            p1 = mt_obj.plot_mt_response(fig_num=6, plot_num=2)
            p1.save_plot(
                edi_path.joinpath(f"{mt_obj.station}.png"),
                fig_dpi=300,
                close_plot=True,
            )

            et = MTime().now()

            diff = pd.Timedelta(et - st, unit="s")
            logger.warning(
                "Processing took: {} minutes", str(diff).split("days")[-1].strip()
            )
            plt.close("all")
            close_open_files()

            logger.info("Completed processing for {}", station_id)

        except Exception as e:
            logger.error("Processing failed for station {}", station_id)
            logger.exception(e)
            close_open_files()
            # continue silently to next station
            continue

# =============================================================================
# Teardown
# =============================================================================
# Remove station sinks and master/console sinks (optional, good practice)
for sid, sink in station_sink_ids.items():
    logger.remove(sink)

logger.remove(master_sink_id)
# logger.remove(console_sink_id)
