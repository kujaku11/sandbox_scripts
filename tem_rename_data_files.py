# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 16:41:29 2021

@author: jpeacock
"""
import shutil
from pathlib import Path
import pandas as pd

usf = False
ml = True
# rename usf files
if usf:
    summary_fn = Path(
        r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\TEM\project_summary.csv"
    )
    save_dir = summary_fn.parent.joinpath("tem_usf")
    if not save_dir.exists():
        save_dir.mkdir()

    df = pd.read_csv(summary_fn.as_posix())
    for row in df.itertuples():
        folder = f"Project{row.project}"
        station = f"Station{row.station}"
        station_dir = summary_fn.parent.joinpath(str(folder), str(station))
        usf_fn = list(station_dir.glob("*.usf"))[0]
        new_usf_fn = save_dir.joinpath(f"{row.name}.usf")
        shutil.copy(usf_fn, new_usf_fn)

# rename .ml files
if ml:
    channel_dict = {"1": "HM-RC005", "2": "HM-RC200", "3": "LM-RC005", "4": "LM-RC200"}
    model_dir = Path(
        r"c:\Users\jpeacock\OneDrive - DOI\Geothermal\Umatilla\TEM\Models\blocky"
    )
    save_dir = model_dir.parent.parent.joinpath("tem_tem")
    if not save_dir.exists():
        save_dir.mkdir()
    for folder in model_dir.iterdir():
        ml_files = folder.glob("*.ml.tem")
        for ml_file in ml_files:
            new_fn = save_dir.joinpath(
                f"{folder.name}_{channel_dict[ml_file.stem[-4]]}.tem"
            )
            shutil.copy(ml_file, new_fn)
